import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QComboBox,
)
from PyQt6.QtCore import QThread, pyqtSignal
from core.extractor import AudioExtractor


class ExtractWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, extractor, mode, input_val, output_dir, browser="chrome", cookies_file=None):
        super().__init__()
        self.extractor = extractor
        self.mode = mode
        self.input_val = input_val
        self.output_dir = output_dir
        self.browser = browser
        self.cookies_file = cookies_file

    def run(self):
        try:
            if self.mode == "url":
                result = self.extractor.extract_from_url(
                    self.input_val, self.output_dir,
                    progress_callback=self.progress.emit,
                    browser=self.browser,
                    cookies_file=self.cookies_file
                )
            else:
                self.progress.emit("Конвертация...")
                base = os.path.splitext(
                    os.path.basename(self.input_val)
                )[0]
                output_path = os.path.join(self.output_dir, f"{base}.mp3")
                result = self.extractor.extract_from_file(
                    self.input_val, output_path
                )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TT Music — Extractor")
        self.setMinimumSize(500, 300)
        self.extractor = AudioExtractor()
        self.worker = None
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        url_group = QGroupBox("Ссылка на видео (YouTube / TikTok)")
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://...")
        url_layout.addWidget(self.url_input)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        browser_group = QGroupBox("Браузер для куков (YouTube / TikTok)")
        browser_layout = QVBoxLayout()

        browser_row = QHBoxLayout()
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["chrome", "brave", "edge", "firefox", "opera"])
        self.browser_combo.setCurrentText("brave")
        browser_row.addWidget(QLabel("Браузер:"))
        browser_row.addWidget(self.browser_combo)
        browser_layout.addLayout(browser_row)

        cookie_row = QHBoxLayout()
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText("cookies.txt (необязательно)")
        self.cookie_input.setReadOnly(True)
        cookie_row.addWidget(self.cookie_input)
        self.cookie_btn = QPushButton("Обзор")
        self.cookie_btn.clicked.connect(self._browse_cookie)
        cookie_row.addWidget(self.cookie_btn)
        browser_layout.addLayout(cookie_row)

        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)

        file_group = QGroupBox("Локальный файл")
        file_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Путь к видеофайлу...")
        self.file_input.setReadOnly(True)
        file_layout.addWidget(self.file_input)
        self.browse_btn = QPushButton("Обзор")
        self.browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(self.browse_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        out_group = QGroupBox("Папка для сохранения")
        out_layout = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Папка для MP3...")
        self.output_input.setReadOnly(True)
        out_layout.addWidget(self.output_input)
        self.output_btn = QPushButton("Обзор")
        self.output_btn.clicked.connect(self._browse_output)
        out_layout.addWidget(self.output_btn)
        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        self.extract_btn = QPushButton("Извлечь")
        self.extract_btn.clicked.connect(self._start_extract)
        layout.addWidget(self.extract_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите видеофайл",
            "", "Video Files (*.mp4 *.mkv *.avi *.mov *.webm)"
        )
        if path:
            self.file_input.setText(path)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if path:
            self.output_input.setText(path)

    def _browse_cookie(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл кук",
            "", "Cookie Files (*.txt);;All Files (*)"
        )
        if path:
            self.cookie_input.setText(path)

    def _start_extract(self):
        url = self.url_input.text().strip()
        file_path = self.file_input.text().strip()
        output_dir = self.output_input.text().strip()

        if not output_dir:
            QMessageBox.warning(self, "Ошибка", "Выберите папку для сохранения.")
            return

        if url and file_path:
            QMessageBox.warning(
                self, "Ошибка",
                "Укажите ссылку ИЛИ выберите файл, не оба."
            )
            return

        if not url and not file_path:
            QMessageBox.warning(
                self, "Ошибка",
                "Укажите ссылку или выберите файл."
            )
            return

        if url and not url.startswith(("http://", "https://")):
            QMessageBox.warning(self, "Ошибка", "Некорректная ссылка.")
            return

        if file_path and not os.path.isfile(file_path):
            QMessageBox.warning(self, "Ошибка", "Файл не найден.")
            return

        mode = "url" if url else "file"
        input_val = url if url else file_path

        self.extract_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Обработка...")

        self.worker = ExtractWorker(
            self.extractor, mode, input_val, output_dir,
            browser=self.browser_combo.currentText(),
            cookies_file=self.cookie_input.text().strip() or None
        )
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self._on_progress)
        self.worker.start()

    def _on_finished(self, result):
        self.extract_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Готово: {result}")
        QMessageBox.information(
            self, "Успех",
            f"Аудио извлечено:\n{result}"
        )
        os.startfile(os.path.dirname(result))

    def _on_error(self, msg):
        self.extract_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ошибка")
        QMessageBox.critical(self, "Ошибка", msg)

    def _on_progress(self, text):
        self.status_label.setText(text)
