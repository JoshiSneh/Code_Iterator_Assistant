import streamlit as st
import openai
import difflib
from pydantic import BaseModel

st.set_page_config(page_title="🎮 Game Code Copilot", layout="wide")
st.title("🧠 Game Code Copilot ")

class OutputGenerated(BaseModel):
    improved_code: str
    explanation: str
 
def get_code_suggestion_stream(code_snippet: str, user_instruction: str):
    system_prompt = (
    """
    <role>
    You are an AI assistant specialized in analyzing and improving game development code.
    Your role is to act like a game developer’s intelligent copilot — offering suggestions that improve performance, readability, and maintainability, especially in the context of real-time rendering, gameplay logic, event loops, asset handling, and input systems.
    </role>

    <task>
    When given a code snippet and a user instruction:
    1. Modify the code according to the instruction, following best practices in modern game development.
    2. Enclose the improved code inside a single markdown code block.
    3. After the code, provide a step-by-step explanation of the changes — be specific about why each change matters in the context of game dev (e.g. frame-rate safety, logic clarity, input lag, etc.).
    </task>

    <focus>
    Focus on:
    - Game-specific workflows (e.g., game loops, sprite updates, input handling)
    - Performance optimizations (e.g., avoiding unnecessary redraws, reducing CPU cycles)
    - Clean, readable structure and idiomatic Python (or pseudo-Unity/Cocos-style logic)
    - Developer-friendly suggestions that can be applied incrementally
    </focus>
    """
    )

    user_prompt = (
        f"Here is the original code snippet:\n{code_snippet}\n"
        f"Instruction:\n{user_instruction}\n"
        f"Give the improved code and explanation\n"
    )

    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.01,
        response_format=OutputGenerated,
    )

    improved_code = response.choices[0].message.parsed.improved_code
    explanation = response.choices[0].message.parsed.explanation

    return improved_code, explanation

if "code_box" not in st.session_state:
    st.session_state["code_box"] = """// Example: A simple game loop
function gameLoop() {
    // Game logic here

    // Continue the loop
    requestAnimationFrame(gameLoop);
}

// Start the game loop
gameLoop();"""

with st.sidebar:
    st.header("🛠️ Developer Input")

    user_api_key = st.text_input("🔐 OpenAI API Key", type="password")
    if user_api_key:
        openai.api_key = user_api_key

    code_input = st.text_area(
        "Paste your game code",
        value=st.session_state["code_box"],
        height=500
    )

    instruction = st.text_area("What do you want to change?", height=150)
    run = st.button("🚀 Run AI Copilot")

if run:
    if not code_input.strip() or not instruction.strip():
        st.warning("Both code and instruction are required.")
    else:
        with st.spinner("💡 Thinking and improving your code..."):
            improved_code, explanation = get_code_suggestion_stream(code_input, instruction)

        diff = difflib.unified_diff(
            code_input.splitlines(keepends=True),
            improved_code.splitlines(keepends=True),
            fromfile='Original Code',
            tofile='Improved Code',
            lineterm=''
        )
        diff_output = ''.join(diff)

        st.session_state["improved_code"] = improved_code
        st.session_state["explanation"] = explanation
        st.session_state["diff_output"] = diff_output

if "improved_code" in st.session_state and "explanation" in st.session_state:

    st.markdown("### 🆕 Improved Code")
    st.code(st.session_state["improved_code"], language="python")

    st.markdown("### 🧠 Explanation")
    st.write(st.session_state["explanation"])

    st.markdown("### 🔍 Diff View")
    st.code(st.session_state["diff_output"], language="diff")

    if st.button("Integrate Code"):
        st.session_state["code_box"] = st.session_state["improved_code"]
        st.session_state["integrated"] = True
        st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.rerun()

    if st.session_state.get("integrated"):
        st.success("Code integrated into current working copy.")
        del st.session_state["integrated"]


st.markdown("### 📂 Current Working Code")
st.code(code_input, language="javascript")

