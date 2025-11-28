from setuptools import setup, find_packages

setup(
    name="year-progress-bot",
    version="1.0.0",
    author="Year Progress Bot Developer",
    author_email="developer@example.com",
    description="A Telegram bot that sends daily updates about the year's progress",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==13.15",
        "requests==2.31.0",
        "schedule==1.2.0",
        "python-dotenv==1.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)