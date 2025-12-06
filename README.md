# Quick Start

- Clone repo to your local machine
```
git clone https://github.com/Xujia118/deepResearchAgent.git
```

- Set up venv
```
python -m venv venv
source venv/bin/activate
```

- Install dependencies
```
pip install -r requirements.txt
```

- Create .env and put openAI api key. Don't change OPENAI_API_KEY.
```
OPENAI_API_KEY="your openai api key"
```

- Run the project at root folder
```
python main.py
```

And voila! 
Sometimes it will search for wikipedia first, and it might not be able to locate the info. Just run it again.