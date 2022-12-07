import os
import time
import itertools
import string
import config


def get_files(path):
    """Returns a list of files in a directory"""
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def get_sha1_value(data):
    """Returns a SHA1 hash of the data"""
    import hashlib
    encoded_data = data.encode()
    return hashlib.sha1(encoded_data).hexdigest()

def label_data(file, slow_value,hashvalue):
    """labels the the files in the captcha directory"""
    print("Labeling data...")
    os.rename(f"{config.UNLABELD_DIR}{file}", f"{config.UNLABELD_DIR}{slow_value}_{hashvalue}.png")
    return f"{slow_value}_{hashvalue}.png"

def move_to_training_file(file):
    """moves the files to the training directory"""
    print("Moving to training directory...")
    os.rename(f".{config.UNLABELD_DIR}{file}", f"{config.DATA_DIR}{file}")

def send_discord_img(img, value, operation_time):
    from discord_webhook import DiscordWebhook, DiscordEmbed
    webhook = DiscordWebhook(url=config.DICSWEBHOOKAICHAT)
    with open (f"{config.DATA_DIR}/{img}", "rb") as f:
        webhook.add_file(file=f.read(), filename="filename.png")
    embed = DiscordEmbed(title=f'{value}', description=f'New data added to training data, time {operation_time:.2f} sec', color=242424)
    embed.set_thumbnail(url=f"attachment://filename.png")
    webhook.add_embed(embed)
    print(webhook.execute())

def log_time(time):
    with open("log.txt", "a") as f:
        f.write(f"{time:.2f},")

def get_train_data():
    for file in get_files({config.UNLABELD_DIR}):
        """loop through the files in the captcha directory"""
        print(f"Processing {file}")
        hash_value = file.split(".png")[0][:]
        is_vaild = True
        start = time.perf_counter()
        while is_vaild:
            for guess in itertools.product(string.ascii_lowercase + string.digits, repeat=5):
                slow_value = ''.join(guess)
                ai_guess = get_sha1_value((slow_value))
                if ai_guess == hash_value:
                    """if the ai guess is correct, relabel and move the file to the training directory"""
                    move_to_training_file(label_data(file, slow_value, hash_value))
                    print(f"[+] New data added {slow_value}_{hash_value}.png")
                    is_vaild = False
                    end = time.perf_counter() - start
                    print(f"Time taken: {end:.4f}s")
                    send_discord_img(f"{slow_value}_{hash_value}.png", slow_value, operation_time=end)
                    log_time(end)
                    break
            if is_vaild == False:
                break

if __name__ == "__main__":
    get_train_data()