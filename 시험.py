import sys
import random
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QRadioButton, QButtonGroup, 
                            QMessageBox, QProgressBar, QComboBox, QShortcut)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class SpanishQuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("스페인어 단어 퀴즈")
        self.setGeometry(100, 100, 800, 600)
        
        # DB 경로 설정
        self.words_db_path = r"\\10.193.232.18\Java\우현 테스트\spanish_words.db"
        self.grammar_db_path = r"\\10.193.232.18\Java\우현 테스트\spanish_grammar.db"
        
        # DB 연결
        self.conn = sqlite3.connect(self.words_db_path)
        self.cursor = self.conn.cursor()
        
        # 퀴즈 상태 초기화
        self.current_question = 0
        self.score = 0
        self.total_questions = 20
        
        # 메인 위젯 설정
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        
        # 문제 유형 선택 추가
        self.type_combo = QComboBox()
        self.type_combo.addItems(["단어", "문법"])
        self.type_combo.currentTextChanged.connect(self.load_words)
        self.layout.insertWidget(0, QLabel("문제 유형:"))
        self.layout.insertWidget(1, self.type_combo)
        
        # 카테고리 선택
        self.category_combo = QComboBox()
        self.load_categories()
        self.category_combo.currentTextChanged.connect(self.load_words)
        self.layout.addWidget(self.category_combo)
        
        # 난이도 선택
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["ALL", "BEGINNER", "INTERMEDIATE"])
        self.difficulty_combo.currentTextChanged.connect(self.load_words)
        self.layout.addWidget(self.difficulty_combo)
        
        # 진행 상황 표시
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)
        self.progress_bar.setMaximum(self.total_questions)
        
        # 점수 표시
        self.score_label = QLabel("점수: 0")
        self.score_label.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.score_label)
        
        # 문제 표시
        self.question_label = QLabel()
        self.question_label.setFont(QFont('Arial', 20))
        self.question_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.question_label)
        
        # 보기 버튼 그룹
        self.button_group = QButtonGroup()
        self.option_buttons = []
        
        # "모름" 라디오 버튼 추가
        self.dont_know_radio = QRadioButton("모름")
        self.button_group.addButton(self.dont_know_radio, 4)  # 인덱스 4를 "모름" 옵션으로 사용
        self.layout.addWidget(self.dont_know_radio)
        
        # 나머지 보기 버튼들
        for i in range(4):
            radio_btn = QRadioButton()
            self.option_buttons.append(radio_btn)
            self.button_group.addButton(radio_btn, i)
            self.layout.addWidget(radio_btn)
        
        # 제출 버튼
        self.submit_button = QPushButton("정답 제출")
        self.submit_button.clicked.connect(self.check_answer)
        self.layout.addWidget(self.submit_button)
        
        # 다음 문제 버튼 추가
        self.next_button = QPushButton("다음 문제")
        self.next_button.clicked.connect(self.next_question)
        self.next_button.setEnabled(False)  # 초기에는 비활성화
        self.layout.addWidget(self.next_button)
        
        # 결과 메시지 레이블 추가
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.result_label)
        
        # 문법 설명 레이블 추가
        self.explanation_label = QLabel("")
        self.explanation_label.setWordWrap(True)  # 자동 줄바꿈
        self.explanation_label.setAlignment(Qt.AlignCenter)
        self.explanation_label.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.explanation_label)
        
        self.central_widget.setLayout(self.layout)
        
        # 첫 문제 로드
        self.load_words()
        self.show_question()
        
        # 키 이벤트 처리를 위한 단축키 설정
        self.next_shortcut = QShortcut(Qt.Key_Return, self)  # Enter 키
        self.next_shortcut.activated.connect(self.handle_enter_key)
        
        # Enter 키 대체 단축키 (숫자 키패드의 Enter)
        self.next_shortcut_keypad = QShortcut(Qt.Key_Enter, self)
        self.next_shortcut_keypad.activated.connect(self.handle_enter_key)
    
    def load_categories(self):
        self.cursor.execute('SELECT DISTINCT category FROM spanish_words')
        categories = ["ALL"] + [row[0] for row in self.cursor.fetchall()]
        self.category_combo.addItems(categories)
    
    def load_words(self):
        category = self.category_combo.currentText()
        difficulty = self.difficulty_combo.currentText()
        quiz_type = self.type_combo.currentText()
        
        if quiz_type == "단어":
            conn = sqlite3.connect(self.words_db_path)
        else:  # 문법
            conn = sqlite3.connect(self.grammar_db_path)
        
        cursor = conn.cursor()
        
        if quiz_type == "단어":
            # 기본 쿼리 수정 - count를 기준으로 정렬 추가
            if category == "ALL" and difficulty == "ALL":
                cursor.execute('''
                    SELECT spanish, korean 
                    FROM spanish_words 
                    ORDER BY COALESCE(count, 0) ASC, RANDOM()
                ''')
            elif category == "ALL":
                cursor.execute('''
                    SELECT spanish, korean 
                    FROM spanish_words 
                    WHERE difficulty = ? 
                    ORDER BY COALESCE(count, 0) ASC, RANDOM()
                ''', (difficulty,))
            elif difficulty == "ALL":
                cursor.execute('''
                    SELECT spanish, korean 
                    FROM spanish_words 
                    WHERE category = ? 
                    ORDER BY COALESCE(count, 0) ASC, RANDOM()
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT spanish, korean 
                    FROM spanish_words 
                    WHERE category = ? AND difficulty = ? 
                    ORDER BY COALESCE(count, 0) ASC, RANDOM()
                ''', (category, difficulty))
        
        else:  # 문법
            if category == "ALL" and difficulty == "ALL":
                cursor.execute('''
                    SELECT question, correct_sentence, wrong_sentence1, 
                           wrong_sentence2, wrong_sentence3, explanation 
                    FROM spanish_grammar 
                    ORDER BY COALESCE(count, 0) ASC, RANDOM()
                ''')
            elif category == "ALL":
                cursor.execute('''
                    SELECT question, correct_sentence, wrong_sentence1, 
                           wrong_sentence2, wrong_sentence3, explanation 
                    FROM spanish_grammar 
                    WHERE difficulty = ? 
                    ORDER BY COALESCE(count, 0) ASC, RANDOM()
                ''', (difficulty,))
            else:
                cursor.execute('''
                    SELECT question, correct_sentence, wrong_sentence1, 
                           wrong_sentence2, wrong_sentence3, explanation 
                    FROM spanish_grammar 
                    WHERE category = ? AND difficulty = ? 
                    ORDER BY COALESCE(count, 0) ASC, RANDOM()
                ''', (category, difficulty))
        
        self.words = cursor.fetchall()
        conn.close()
        
        self.current_question = 0
        self.score = 0
        self.score_label.setText("점수: 0")
        self.show_question()
    
    def show_question(self):
        if self.current_question < self.total_questions and self.words:
            quiz_type = self.type_combo.currentText()
            
            if quiz_type == "단어":
                # 데이터베이스에서 가져온 단어의 수가 충분한지 확인
                if len(self.words) <= self.current_question:
                    QMessageBox.warning(self, "경고", "데이터베이스에 충분한 단어가 없습니다!")
                    self.show_result()
                    return
                
                # 현재 단어와 정답
                word, correct_answer = self.words[self.current_question]
                self.question_label.setText(f"'{word}'의 뜻은?")
                
                # 현재 카테고리 확인
                self.cursor.execute('SELECT category FROM spanish_words WHERE spanish = ?', (word,))
                current_category = self.cursor.fetchone()[0]
                
                # 보기 생성
                options = [correct_answer]
                while len(options) < 4:
                    if current_category == "숫자":
                        # 숫자 카테고리인 경우 숫자 보기만 가져오기
                        self.cursor.execute('''
                            SELECT korean 
                            FROM spanish_words 
                            WHERE category = "숫자" 
                            AND korean != ? 
                            ORDER BY RANDOM() 
                            LIMIT 1
                        ''', (correct_answer,))
                    else:
                        # 다른 카테고리의 경우 같은 카테고리에서 보기 가져오기
                        self.cursor.execute('''
                            SELECT korean 
                            FROM spanish_words 
                            WHERE category = ? 
                            AND korean != ? 
                            ORDER BY RANDOM() 
                            LIMIT 1
                        ''', (current_category, correct_answer))
                    
                    random_answer = self.cursor.fetchone()
                    if random_answer and random_answer[0] not in options:
                        options.append(random_answer[0])
                
                # 보기 섞기
                random.shuffle(options)
                self.correct_option = options.index(correct_answer)
                
                # 보기 버튼에 텍스트 설정
                for i, option in enumerate(options):
                    self.option_buttons[i].setText(option)
            
            else:  # 문법
                question, correct_answer, wrong1, wrong2, wrong3, explanation = self.words[self.current_question]
                self.question_label.setText(question)
                
                # 보기 생성
                options = [correct_answer, wrong1, wrong2, wrong3]
                random.shuffle(options)
                self.correct_option = options.index(correct_answer)
                
                # 보기 버튼에 텍스트 설정
                for i, option in enumerate(options):
                    self.option_buttons[i].setText(option)
            
            # 진행 상황 업데이트
            self.progress_bar.setValue(self.current_question)
        else:
            self.show_result()
    
    def check_answer(self):
        if self.button_group.checkedId() == -1:
            QMessageBox.warning(self, "경고", "답을 선택해주세요!")
            return
        
        quiz_type = self.type_combo.currentText()
        current_word = self.words[self.current_question][0]
        
        # "모름" 선택 처리
        if self.button_group.checkedId() == 4:
            if quiz_type == "단어":
                self.cursor.execute('''
                    UPDATE spanish_words 
                    SET wrong = COALESCE(wrong, 0) + 1,
                        count = COALESCE(count, 0) + 1
                    WHERE spanish = ?
                ''', (current_word,))
                self.result_label.setText(f"정답은 '{self.words[self.current_question][1]}'입니다. 📚")
            else:
                self.result_label.setText(f"정답은 '{self.words[self.current_question][1]}'입니다. 📚")
                self.explanation_label.setText(self.words[self.current_question][5])
            self.result_label.setStyleSheet("color: blue;")
        else:
            if quiz_type == "단어":
                # 기존 단어 퀴즈 로직
                if self.button_group.checkedId() == self.correct_option:
                    self.score += 1
                    self.score_label.setText(f"점수: {self.score}")
                    self.result_label.setText("정답입니다! 🎉")
                    self.result_label.setStyleSheet("color: green;")
                    self.next_button.setEnabled(True)
                else:
                    self.result_label.setText(f"틀렸습니다. 정답은 '{self.words[self.current_question][1]}'입니다. 😢")
                    self.result_label.setStyleSheet("color: red;")
            else:  # 문법
                if self.button_group.checkedId() == self.correct_option:
                    self.score += 1
                    self.score_label.setText(f"점수: {self.score}")
                    self.result_label.setText("정답입니다! 🎉")
                    self.result_label.setStyleSheet("color: green;")
                    self.explanation_label.setText("잘 하셨습니다!")
                    self.next_button.setEnabled(True)
                else:
                    self.result_label.setText("틀렸습니다. 😢")
                    self.result_label.setStyleSheet("color: red;")
                    self.explanation_label.setText(f"정답: {self.words[self.current_question][1]}\n\n"
                                                f"설명: {self.words[self.current_question][5]}")
        
        # 답안 선택 비활성화
        for button in self.option_buttons:
            button.setEnabled(False)
        self.dont_know_radio.setEnabled(False)
        self.submit_button.setEnabled(False)
        self.next_button.setEnabled(True)
    
    def next_question(self):
        # 다음 문제로 이동
        self.current_question += 1
        
        # 버튼 상태 초기화
        self.button_group.setExclusive(False)
        for button in self.option_buttons:
            button.setChecked(False)
            button.setEnabled(True)
        self.dont_know_radio.setChecked(False)
        self.dont_know_radio.setEnabled(True)
        self.button_group.setExclusive(True)
        
        # 레이블 초기화
        self.result_label.setText("")
        self.explanation_label.setText("")
        
        # 버튼 상태 설정
        self.submit_button.setEnabled(True)
        self.next_button.setEnabled(False)
        
        self.show_question()
    
    def show_result(self):
        score_percentage = (self.score / self.total_questions) * 100
        QMessageBox.information(self, "퀴즈 종료", 
            f"퀴즈가 끝났습니다!\n"
            f"총 {self.total_questions}문제 중 {self.score}개 맞추셨습니다.\n"
            f"정답률: {score_percentage:.1f}%")
        
        reply = QMessageBox.question(self, "다시 하기", 
            "다시 도전하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.load_words()
        else:
            self.close()
    
    def closeEvent(self, event):
        self.conn.close()
        event.accept()
    
    def handle_enter_key(self):
        # 답을 선택하지 않은 상태에서 Enter를 누른 경우
        if not self.submit_button.isEnabled() and self.next_button.isEnabled():
            self.next_question()
        # 답을 선택한 상태에서 Enter를 누른 경우
        elif self.submit_button.isEnabled() and not self.next_button.isEnabled():
            if self.button_group.checkedId() != -1:  # 답이 선택되었을 때만
                self.check_answer()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpanishQuizApp()
    window.show()
    sys.exit(app.exec_())
 