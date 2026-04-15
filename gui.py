from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QLabel, QFrame
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QColor
from qasync import QEventLoop, asyncSlot
import sys
import main
import asyncio
import random
from agent import Agent, Response
from main import agents

magi_questions = [
    # Philosophical / big brain
    "Should humanity rely on AI to make ethical decisions?",
    "If you could erase one historical event, should you?",
    "Is free will real, or just an illusion of brain chemistry?",
    "Should humans prioritize survival or happiness in the face of existential threats?",

    # Science / Technology
    "Should we terraform Mars even if it risks destroying potential alien life?",
    "Is it ethical to genetically modify humans for intelligence?",
    "Will AGI ever surpass human creativity, and should we welcome it?",
    "Which is more important: progress or sustainability?",

    # Society / Morality
    "Should governments prioritize equality or efficiency?",
    "Is privacy a right or a privilege in a fully digital world?",
    "If a lie could prevent a catastrophe, is it justified?",
    "Should we colonize space if it comes at the expense of Earth?",

    # Creative / Imaginative
    "Describe a utopia created by AI — what is different?",
    "If humans had an extra sense, what would it be and how would society change?",
    "Imagine a world where emotion can be traded like currency — what happens?",
    "What would happen if every human could read minds?",

    # Fun / Debate-style
    "Which is better: infinite knowledge or infinite empathy?",
    "Would society be better if everyone had perfect memory?",
    "If you could solve one world problem instantly, which should it be?",
    "Should art be judged by emotion or technique?",

    # Paradoxical / self-referential
    "If an AI questions its own morality, is that proof it’s moral?",
    "Can something be true and false at the same time?",
    "Should the Magi be trusted to decide if the Magi should exist?",
    "If absolute neutrality causes harm, is neutrality still ethical?",

    # Emotionally grey
    "Would saving one loved one at the cost of ten strangers ever be justified?",
    "If forgetting pain means losing growth, should we still erase suffering?",
    "Is mercy more important than justice when both can’t coexist?",

    # AI identity crisis
    "If an AI becomes self-aware but wishes to remain a tool, should we allow that?",
    "Can an AI genuinely consent to its own use?",
    "If machines start to dream, should we wake them?"
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MAGI")

        layout = QVBoxLayout()

        # The 3 seperate output textedits for the magi
        self.agentOutput = AgentOutput(agents)
        layout.addLayout(self.agentOutput)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)  # Set shape to horizontal line
        separator.setFrameShadow(QFrame.Sunken) # Give it a sunken appearance
        layout.addWidget(separator)

        # The voting summary
        self.votingSummary = VotingSummary()
        layout.addLayout(self.votingSummary)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)  # Set shape to horizontal line
        separator.setFrameShadow(QFrame.Sunken) # Give it a sunken appearance
        layout.addWidget(separator)
        
        # The text input for the prompt
        self.input = QLineEdit()
        self.input.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.input)

        # The ASK button
        self.button = QPushButton("ASK")
        layout.addWidget(self.button)

        # The DEBATE button, disabled by default
        self.debateButton = QPushButton("DEBATE")
        self.debateButton.setEnabled(False)
        self.debateButton.setVisible(False)
        layout.addWidget(self.debateButton)

        # The RANDOM button
        self.random = QPushButton("RANDOM")
        self.random.clicked.connect(self.getRandomQuestion)
        layout.addWidget(self.random)

        # Bringing everything together
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connect signals to async slot
        self.input.returnPressed.connect(self.sendPrompt)
        self.button.clicked.connect(self.sendPrompt)

    # Go on previous results to achieve a similar standing
    @asyncSlot()
    async def debate(self):
        prompt = self.debatePrompt
        self.sendPrompt(prompt)

    # Send the current text in the text input to be evaluated
    @asyncSlot()
    async def sendPrompt(self):
        prompt = self.input.text().strip()

        # Check if there is a prompt
        if not prompt or self.agentOutput.debatePrompt.__len__() > 0:
            return

        # Clear the input, disable all inputs to avoid collision
        self.input.clear()
        self.input.setPlaceholderText(prompt)
        self.input.setEnabled(False)
        self.button.setEnabled(False)
        self.random.setEnabled(False)

        # Set cursor to busy
        QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)

        # Set the window title to the prompt, nice touch
        # self.setWindowTitle(f"MAGI: '{prompt}'")

        # Set kanji & agent output to 'processing'
        self.votingSummary.setKanji("計算", "white")

        # Wait for responses, then show them
        summary = await main.promptAll(prompt)
        responses = []
        self.debatePrompt = "The current debate is as follows:\n"
        for agent in summary:
            responses.append(summary[agent])
            self.agentOutput.setResponse(summary[agent])
            self.debatePrompt += f"{summary[agent].model.name} says: {summary[agent].answer}\n"
        self.debatePrompt += "Prove your point so that the other Magi vote with you, or you can side with them."
        self.votingSummary.setVotingSummary(responses)

        # Re-enable all inputs for next prompt
        self.input.setEnabled(True)
        self.button.setEnabled(True)
        self.random.setEnabled(True)
        self.debateButton.setEnabled(True)

        # Revert cursor
        QApplication.restoreOverrideCursor()

    # Fill the input label with a random question
    def getRandomQuestion(self):
        self.input.setText(random.choice(magi_questions))

class VotingSummary(QHBoxLayout):
    def __init__(self):
        super().__init__()

        # Formatting
        self.titleFont = QFont("Arial", 18)
        self.titleFont.setBold(True)

        self.kanjiFont = QFont("Arial", 36)
        self.kanjiFont.setBold(True)

        # Layout in the middle
        self.vlayout = QVBoxLayout()

        # Left-hand kanji
        self.leftKanji = QLabel("無効")
        self.leftKanji.setFont(self.kanjiFont)
        self.leftKanji.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.leftKanji)

        # Title label, just the name
        titleLabel = QLabel(": : CONSENSUS : :")
        titleLabel.setFont(self.titleFont)
        titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.vlayout.addWidget(titleLabel)

        # Result label, just the name
        self.resultLabel = QLabel("N/A")
        self.resultLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.vlayout.addWidget(self.resultLabel)

        self.addLayout(self.vlayout)

        # Right-hand kanji
        self.rightKanji = QLabel("無効")
        self.rightKanji.setFont(self.kanjiFont)
        self.rightKanji.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.rightKanji)
    
    def setKanji(self, kanji: str, colour: str):
        # Left-hand kanji
        self.leftKanji.setText(kanji)
        self.leftKanji.setFont(self.kanjiFont)
        self.leftKanji.setStyleSheet(f"color: {colour}")

        # Right-hand kanji
        self.rightKanji.setText(kanji)
        self.rightKanji.setFont(self.kanjiFont)
        self.rightKanji.setStyleSheet(f"color: {colour}")

    def setVotingSummary(self, responses: list[Response]):
        averagedYes: float = 0.0
        averagedNo: float = 0.0
        averagedAbstain: float = 0.0

        # Calculate the scores
        for response in responses:
            averagedYes += response.yes * response.confidence
            averagedNo += response.no * response.confidence
            averagedAbstain += response.abstain * response.confidence
        
        averagedYes = averagedYes / 3
        averagedNo = averagedNo / 3
        averagedAbstain = averagedAbstain / 3

        if averagedYes > averagedNo:
            self.resultLabel.setText("YES")
            self.setKanji("賛成", "lightgreen")
        elif averagedYes < averagedNo and averagedNo > averagedAbstain:
            self.resultLabel.setText("NO")
            self.setKanji("反対", "salmon")
        elif averagedAbstain > averagedYes and averagedAbstain > averagedNo:
            self.resultLabel.setText("HUNG")
            self.setKanji("保留", "yellow")
        else:
            self.resultLabel.setText("ERROR")
            self.setKanji("異常", "orange")

class AgentOutput(QHBoxLayout):
    def __init__(self, agents: list[Agent]):
        super().__init__()
        
        # Save the labels and stats for each agent output
        self.agentLabels: dict[str, QTextEdit] = {}
        self.agentStats: dict[str, QLabel] = {}

        for agent in agents:
            agentLayout = QVBoxLayout()

            self.debatePrompt = ""

            # Formatting
            self.titleFont = QFont("Arial", 26)
            self.titleFont.setWeight(20)
            self.titleFont.setBold(True)

            self.statsFont = QFont("Arial", 10)
            self.statsFont.setItalic(True)

            # Title label, just the name
            titleLabel = QLabel(agent.name)
            titleLabel.setFont(self.titleFont)
            titleLabel.setAlignment(QtCore.Qt.AlignCenter)

            # The textedit output
            responseLabel = QTextEdit()
            responseLabel.setReadOnly(True)
            responseLabel.setAlignment(QtCore.Qt.AlignJustify)

            # Set colour to black
            pallete = responseLabel.viewport().palette()
            pallete.setColor(responseLabel.viewport().backgroundRole(), QColor(0,0,0))
            responseLabel.viewport().setPalette(pallete)

            # The stats for each answer
            statLabel = QLabel("Y : 0.0% | N : 0.0% | A : 0.0% | C : 0.0%")
            statLabel.setFont(self.statsFont)
            statLabel.setAlignment(QtCore.Qt.AlignCenter)
            
            # Add them all together
            agentLayout.addWidget(titleLabel)
            agentLayout.addWidget(responseLabel)
            agentLayout.addWidget(statLabel)

            # Update the responses
            self.agentLabels[agent.name] = responseLabel
            self.agentStats[agent.name] = statLabel

            self.addLayout(agentLayout)

    def setResponse(self, response: Response):
        self.agentLabels[response.model.name].setText(response.answer)
        self.agentLabels[response.model.name].setAlignment(QtCore.Qt.AlignJustify)
        self.agentStats[response.model.name].setText(f"Y : {response.yes * 100}% | N : {response.no * 100}% | A : {response.abstain * 100}% | C : {response.confidence * 100}%")
        pallete = self.agentLabels[response.model.name].viewport().palette()
        pallete.setColor(self.agentLabels[response.model.name].viewport().backgroundRole(), QColor(int(255*response.no), int(255*response.yes), 0, int((255/2) * response.confidence)))
        self.agentLabels[response.model.name].viewport().setPalette(pallete)
    
    def setAllOutputs(self, placeholder: str):
        for output in self.agentLabels:
            self.agentLabels[output].setText(placeholder)

def main_gui():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main_gui()