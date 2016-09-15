# chatter-data-pump

Use this script to simulate an active Salesforce Chatter deployment. It continuously posts Chatter threads using a dataset from an American town's Facebook group.

To add some variety, it:
  * Chooses random users in your org to create the posts.
  * Chooses random users, groups, and accounts to post to (you can easily expand this to include more objects).
  * Chooses random threads from the Facebook dataset.

## Installation

```
pip install -r requirements.txt
cp env.template .env
```

And then edit your `.env` file to configure your Salesforce login settings. You'll need to obtain your [Salesforce security token](https://help.salesforce.com/apex/HTViewHelpDoc?id=user_security_token.htm) for the `SFDC_TOKEN` value.

### Obtaining the dataset

The dataset is a publicly available archive of a Facebook group, and is hosted by the data science competition site Kaggle. Once you register for a free account, download the `cheltenham-s-facebook-group.zip` file from the [Cheltenham Facebook Group dataset page](https://www.kaggle.com/mchirico/cheltenham-s-facebook-group), extract the `cheltenham-facebook-group.sqlite` file, and place it in the same directory as `data_pump.py`.

## Running the script
```
python data_pump.py
```

The feed items and comments being posted to your Salesforce org will also be output to the console.

## Limitations

The script only makes text posts. The tool could be improved by adding support for things like:

  * @mentions
  * Likes on feed items and comments
  * Rich text
  * Topics
  * File attachments
  * Link attachments
  * Communities
  * etc.
