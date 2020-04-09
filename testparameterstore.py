import os, traceback, json, configparser, boto3

# Initialize boto3 client at global scope for connection reuse
client = boto3.client('ssm')
env = os.environ['ENV']
app_config_path = os.environ['APP_CONFIG_PATH']
full_config_path = '/' + env + '/' + app_config_path

def lambda_handler(event, context):
    global app
    # Initialize app if it doesn't yet exist

    print("Loading config and creating new MyApp...")
    print("Config Path:" + full_config_path)

    param_details = client.get_parameters_by_path(
            Path=full_config_path,
            Recursive=False,
            WithDecryption=True
        )
    print(param_details)
