Read Me: ivy_reporting.py

Script assumes .csv file exported from Ivy.ai with following filters:
Chat Length, Messages to Bot, Bot Responses (Generative),
Bot Responses (Retrieval), Bot Responses (Low Confidence),
Bot Responses (No Confidence)

Note that Data Lake exports prior to November 2023 will not include reporting
of generative responses or retrieval responses. Instead,
TOTAL [total messages or total chats? TBD] - low confidence - no confidence may
be used as a proxy. 



