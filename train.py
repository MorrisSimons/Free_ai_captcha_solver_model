import os
import glob
import torch
import numpy as np

from sklearn import preprocessing
from sklearn import model_selection
from sklearn import metrics

import config
import dataset
import engine
from model import CaptchaModel

def run_training():
    image_files = glob.glob(os.path.join(config.DATADIR, "*.png"))
    targets_orig = [x.split("/")[-1][9:14] for x in image_files]
    targets = [[c for c in x] for x in targets_orig]
    targets_flat = [c for clist in targets for c in clist]
    lbl_enc = preprocessing.LabelEncoder()
    lbl_enc.fit(targets_flat)
    targets_enc = [lbl_enc.transform(x) for x in targets]
    target_enc = np.array(targets_enc) + 1
    #print(targets) # it's a list of lists of characters
    #print(np.unique(targets_flat)) # it's a list of all the unique characters in the captcha
    print(target_enc)
    print(len(lbl_enc.classes_)) # it's the number of unique characters in the captcha
    (
     train_imgs,
     test_imgs,
     train_targets,
     test_targets,
     train_orig_targets,
     test_orig_targets
     ) = model_selection.train_test_split(
        image_files,
        target_enc,
        targets_orig,
        test_size=0.1,
        random_state=42
    )
    train_dataset = dataset.ClassificationDataset(
        image_paths=train_imgs,
        targets=train_targets,
        resize=(config.IMAGE_HEIGHT,
                config.IMAGE_WIDTH
                ),)
    test_dataset = dataset.ClassificationDataset(
        image_paths=train_imgs,
        targets=train_targets,
        resize=(config.IMAGE_HEIGHT,
                config.IMAGE_WIDTH
                ),)
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=config.BATCH_SIZE,
        num_workers=config.NUM_WORKERS,
        shuffle = True,
        )
    test_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=config.BATCH_SIZE,
        num_workers=config.NUM_WORKERS,
        shuffle = False,
        )
    
    model = CaptchaModel(num_chars=len(lbl_enc.classes_))
    model.to(config.DEVICE)

    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        patience=5,
        factor=0.8,
        verbose=True,
        )
    for epoch in range(config.EPOCHS):
        train_loss = engine.train_fn(model, train_loader, optimizer)
        valid_preds, valid_loss = engine.eval_fn(model, test_loader)
        
    """Adam is a replacement optimization algorithm for stochastic gradient descent for training deep learning
    models. Adam combines the best properties of the AdaGrad
    and RMSProp algorithms to provide an optimization algorithm that can handle sparse
    gradients on noisy problems."""


if __name__ == "__main__":
    run_training()

