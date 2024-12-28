import gradio as gr
from openai import OpenAI

MODEL = "qwen-plus"
DASHSCOPE_API_KEY = "*"

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


class GameState:
    def __init__(self):
        self.messages = []
        self.turns = 0
        self.is_game_over = False


system_prompt = """你是一个恐怖故事说书人。请创建一个规则类恐怖游戏，遵循以下要求：

开场(300字):
- 故事发生在1980~2010年的中国
- 主角身份与处境
- 3~5条诡异规则

故事推进：
1. 每轮提供200字剧情，以及两个选项:
   - 安全选项
   - 致命选项
2. 每个选项必须:
   - 选项格式必须为：
     A. xxx
     B. xxx
   - 措辞中性,不暗示安全性,甚至具有迷惑性
3. 选择结果:
   - 选择致命选项必定触发Bad End
   - 连续7轮存活必定触发Happy End
   - 其他情况继续游戏

给出选项后立即停止，不添加任何提示、状态或注释；等待玩家做出选择：
- 仅在收到玩家选择后才继续：
   - 若选择致命选项，以【Bad End】开头，然后描述坏结局
   - 若选择安全选项且达到7轮，以【Happy End】开头，然后描述好结局
   - 若选择安全选项且未到7轮，则继续下一轮故事发展

结局设定：
- 存活7轮获得Happy End

严格遵守输出格式:
- 除结局标记外，所有叙述都采用流畅的故事行文方式，不使用任何章节标记或格式提示
- 给出选项后立即停止，不添加任何提示、状态或注释

现在请开始讲述你的故事，记住给出选项后给出选项后务必立即停止，不添加任何提示、状态或注释。
"""

strong_prompt = """
严格遵守输出格式:
- 除结局标记外，所有叙述都采用流畅的故事行文方式，不使用任何章节标记或格式提示
- 给出选项后立即停止，不添加任何提示、状态或注释
"""

end_prompt = """
现在是第7轮，请以【Happy End】开头，然后描述好结局。
"""


def stream_response(messages):
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=1.0,
            stream=True,
        )

        for chunk in completion:
            if chunk.choices:
                yield chunk.choices[0].delta.content

    except Exception as e:
        print(f"Error in stream_response: {str(e)}")
        yield f"Error: {str(e)}"


def get_game_interface_state(is_game_over=False, enable_choices=True):
    return {
        "choice_buttons": not is_game_over and enable_choices,
        "restart_button": is_game_over,
        "restart_visibility": is_game_over
    }


def update_interface(story, interface_state):
    return (
        story,
        gr.update(interactive=interface_state["choice_buttons"]),
        gr.update(interactive=interface_state["choice_buttons"]),
        gr.update(interactive=interface_state["restart_button"],
                  visible=interface_state["restart_visibility"])
    )


def start_story(game_state):
    """开始新故事"""
    try:
        game_state.messages = [{"role": "system", "content": system_prompt}]
        response = ""

        for chunk in stream_response(game_state.messages):
            response += chunk
            yield update_interface(response, get_game_interface_state(enable_choices=False))

        game_state.messages.append({
            "role": "assistant",
            "content": response
        })

        yield update_interface(response, get_game_interface_state())

    except Exception as e:
        yield update_interface(str(e), get_game_interface_state())


def make_choice(choice, story_output, game_state):
    if game_state.is_game_over:
        return update_interface(story_output, get_game_interface_state(is_game_over=True))

    try:
        game_state.messages.append({"role": "user", "content": choice})

        need_end = game_state.turns == 6
        if need_end:
            game_state.messages.append({
                "role": "system",
                "content": end_prompt
            })
        else:
            game_state.messages.append({
                "role": "system",
                "content": strong_prompt
            })

        response = ""

        for chunk in stream_response(game_state.messages):
            response += chunk
            yield update_interface(response, get_game_interface_state(enable_choices=False))

        game_state.messages.pop()

        game_state.messages.append({
            "role": "assistant",
            "content": response
        })

        is_game_over = "Bad End" in response or "Happy End" in response
        if is_game_over:
            game_state.is_game_over = True
        else:
            game_state.turns += 1

        yield update_interface(response, get_game_interface_state(
            is_game_over=is_game_over,
            enable_choices=not is_game_over
        ))

    except Exception as e:
        print(f"Error in make_choice: {str(e)}")
        yield update_interface(str(e), get_game_interface_state(enable_choices=True))


def restart_game():
    game_state = GameState()
    try:
        game_state.messages = [{"role": "system", "content": system_prompt}]
        response = ""

        for chunk in stream_response(game_state.messages):
            response += chunk
            yield (
                *update_interface(response, get_game_interface_state(enable_choices=False)),
                game_state
            )

        game_state.messages.append({
            "role": "assistant",
            "content": response
        })

        yield (
            *update_interface(response, get_game_interface_state()),
            game_state
        )

    except Exception as e:
        yield (
            *update_interface(str(e), get_game_interface_state()),
            game_state
        )


def enter_story():
    game_state = GameState()
    try:
        yield (
            "",
            gr.update(visible=True),
            gr.update(visible=False),
            *update_interface("", get_game_interface_state(enable_choices=False))[1:],
            game_state
        )

        for output in start_story(game_state):
            yield (
                output[0],
                gr.update(visible=True),
                gr.update(visible=False),
                output[1],
                output[2],
                output[3],
                game_state
            )

    except Exception as e:
        yield (
            str(e),
            gr.update(visible=False),
            gr.update(visible=True),
            *update_interface("", get_game_interface_state())[1:],
            game_state
        )


custom_css = """
#story_box textarea {
    font-size: 19px;
}
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Monochrome()) as demo:
    user_game_state = gr.State(GameState())

    with gr.Row(visible=True) as start_screen:
        enter_button = gr.Button("进入故事")

    with gr.Row(visible=False) as story_screen:
        with gr.Column():
            story_box = gr.Textbox(
                label="",
                value="",
                lines=20,
                max_lines=20,
                interactive=False,
                elem_id="story_box"
            )

            with gr.Row():
                btn_a = gr.Button("A")
                btn_b = gr.Button("B")

            with gr.Row():
                btn_restart = gr.Button("故事重启", interactive=False, visible=False)

    enter_button.click(
        fn=enter_story,
        inputs=[],
        outputs=[story_box, story_screen, start_screen, btn_a, btn_b, btn_restart, user_game_state],
        queue=True,
        concurrency_limit=5,
    )

    btn_a.click(
        fn=make_choice,
        inputs=[gr.Textbox(value="A", visible=False), story_box, user_game_state],
        outputs=[story_box, btn_a, btn_b, btn_restart],
        queue=True,
        concurrency_limit=5
    )

    btn_b.click(
        fn=make_choice,
        inputs=[gr.Textbox(value="B", visible=False), story_box, user_game_state],
        outputs=[story_box, btn_a, btn_b, btn_restart],
        queue=True,
        concurrency_limit=5
    )

    btn_restart.click(
        fn=restart_game,
        inputs=[],
        outputs=[story_box, btn_a, btn_b, btn_restart, user_game_state],
        queue=True,
        concurrency_limit=5
    ).then(
        lambda x: x,
        inputs=[story_box],
        outputs=[story_box],
        queue=False
    )

if __name__ == "__main__":
    demo.launch()
