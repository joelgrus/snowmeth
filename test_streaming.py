import asyncio

import dspy

model = "openrouter/google/gemini-2.5-flash-lite-preview-06-17"
# model = "openrouter/openai/gpt-4o-mini"  # For testing with OpenAI


lm = dspy.LM(model, cache=False)
dspy.settings.configure(lm=lm)


module = dspy.Predict("premise -> long_story")


# class MyModule(dspy.Module):
#     def __init__(self):
#         super().__init__()

#         self.tool = dspy.Tool(lambda x: 2 * x, name="double_the_number")
#         self.predict = dspy.ChainOfThought("num1, num2->sum")

#     def forward(self, num, **kwargs):
#         num2 = self.tool(x=num)
#         return self.predict(num1=num, num2=num2)


# class MyStatusMessageProvider(dspy.streaming.StatusMessageProvider):
#     def tool_start_status_message(self, instance, inputs):
#         return f"Calling Tool {instance.name} with inputs {inputs}..."

#     def tool_end_status_message(self, outputs):
#         return f"Tool finished with output: {outputs}!"

# predict = MyModule()

stream_listeners = [
    # dspy.ChainOfThought has a built-in output field called "reasoning".
    dspy.streaming.StreamListener(signature_field_name="long_story"),
]

stream_predict = dspy.streamify(
    module,
    stream_listeners=stream_listeners,
    # status_message_provider=MyStatusMessageProvider(),
)


async def read_output_stream():
    output = stream_predict(
        premise="A brave knight sets out on a quest to save a kingdom from a dragon."
    )

    return_value = None
    async for chunk in output:
        if isinstance(chunk, dspy.streaming.StreamResponse):
            print(chunk)
        elif isinstance(chunk, dspy.Prediction):
            return_value = chunk
        elif isinstance(chunk, dspy.streaming.StatusMessage):
            print(chunk)
    return return_value


program_output = asyncio.run(read_output_stream())
print("Final output: ", program_output)
