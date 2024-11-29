# Use the official AWS Lambda Python 3.9 runtime base image
FROM public.ecr.aws/lambda/python:3.9

# Copy application code and dependencies into the container
COPY . ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip install boto3 openai

# Set the default command for Lambda to invoke the function
CMD ["lambda_function.lambda_handler"]
