import dspy

lm = dspy.LM(model="openrouter/google/gemini-2.5-flash-lite-preview-06-17")
dspy.configure(lm=lm)


class CountR(dspy.Signature):
    text: str = dspy.InputField()
    count: int = dspy.OutputField(desc="Number of R's in the text, case insensitive")


module = dspy.ChainOfThought(CountR)

print("Before optimization:")
print(module(text="strawberry"))

# Create training examples with correct R counts
trainset = [
    dspy.Example(text="raspberry", count=3).with_inputs(
        "text"
    ),  # r-a-s-p-b-e-r-r-y has 3 R's
    dspy.Example(text="cherry", count=2).with_inputs("text"),  # c-h-e-r-r-y has 2 R's
    dspy.Example(text="orange", count=1).with_inputs("text"),  # o-r-a-n-g-e has 1 R
    dspy.Example(text="blueberry", count=3).with_inputs(
        "text"
    ),  # b-l-u-e-b-e-r-r-y has 3 R's
    dspy.Example(text="pear", count=1).with_inputs("text"),  # p-e-a-r has 1 R
    dspy.Example(text="banana", count=0).with_inputs("text"),  # b-a-n-a-n-a has 0 R's
    dspy.Example(text="watermelon", count=1).with_inputs(
        "text"
    ),  # w-a-t-e-r-m-e-l-o-n has 1 R
]

# Use LabeledFewShot optimizer
optimizer = dspy.LabeledFewShot(k=5)  # Use 5 examples
optimized_module = optimizer.compile(module, trainset=trainset)

print("\nAfter optimization:")
print(optimized_module(text="strawberry"))
