import os
import sys
import time
import random
import torch
import torch.backends.cudnn as cudnn
import torch.nn as nn
import torch.nn.init as init
import torch.optim as optim
import torch.utils.data
from torch.cuda.amp import autocast, GradScaler
import numpy as np

from utils import CTCLabelConverter, AttnLabelConverter, Averager
from dataset import hierarchical_dataset, AlignCollate, Batch_Balanced_Dataset
from model import Model
from test import validation

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Log:
    def __init__(self, experiment_name):
        self.__experiment_name = experiment_name
    
    def write_log(self):
        pass

class ValidDatasetLog(Log):
    def __init__(self):
        super().__init__(experiment_name)

    def write_log(self, valid_dataset_log):
        log = open(f'./saved_models/{self.__experiment_name}/log_dataset.txt', 'a', encoding="utf8")
        log.write(valid_dataset_log)
        print('-' * 80)
        log.write('-' * 80 + '\n')
        log.close()


class ValidationLog(Log):
    def __init__(self, experiment_name):
        super().__init__(experiment_name)
        
    def write_log(self, loss_model_log, predicted_result_log):
        with open(f'./save_models/{self.__experiment_name}/log_train.txt', 'a', encoding='utf8') as log:
            loss_model_log = f'{loss_log}\n{current_model_log}\n{best_model_log}'
            log.write(loss_model_log + '\n')
            log.write(predicted_result_log + '\n')
            
            

class Parameter:
    def __init__(self, model):
        self.__model = model
        
    def count_parameters(self):
        print("Modules, Parameters")
        total_params = 0
        for name, parameter in self.__model.named_parameters():
            if not parameter.requires_grad: continue
            param = parameter.numel()
            total_params+=param
            print(name, param)
        print(f"Total Trainable Params: {total_params}")
        return total_params
        
class TrainDatasetProcessor:
    def __init__(self, opt):
        self.__opt = opt    

    def check_data_filtering(self):
        if not self.__opt.data_filtering_off:
            print('Filtering the images containing characters which are not in opt.character')
            print('Filtering the images whose label is longer than opt.batch_max_length')
    
    def __select_data(self):
        self.__opt.select_data = self.__opt.select_data.split('-')
    
    def __set_data_ratio(self):
        self.__opt.batch_ratio = self.__opt.batch_ratio.split('-')
        
    def load_train_dataset(self):
        self.check_data_filtering()
        self.__select_data()
        self.__set_data_ratio()
        train_dataset = Batch_Balanced_Dataset(self.__opt)
        return train_dataset
    
    def get_opt(self):
        return self.__opt


class ValidDatasetProcessor:
    def __init__(self, opt):
        self.__opt = opt
        self.__log = ValidDatasetLog(opt.experiment_name)
    
    def create_valid_dataset(self):
        AlignCollate_valid = AlignCollate(imgH=self.__opt.imgH, imgW=self.__opt.imgW, keep_ratio_with_pad=self.__opt.PAD, contrast_adjust=self.__opt.contrast_adjust)

        valid_dataset, valid_dataset_log = hierarchical_dataset(root=opt.valid_data, opt=opt)
        
        valid_loader = torch.utils.data.DataLoader(
            valid_dataset, batch_size=min(32, opt.batch_size),
            shuffle=True,  # 'True' to check training progress with validation function.
            num_workers=int(opt.workers), prefetch_factor=512,
            collate_fn=AlignCollate_valid, pin_memory=True)
        
        self.__log.write_log(valid_dataset_log)
        
        return valid_loader
    
    def get_opt(self):
        return self.__opt
    
class ModelConfiguration:
    def __init__(self, opt):
        self.__opt = opt
        self.__model = None
        self.__converter = None
        
    def __choose_converter(self):
        if 'CTC' in self.__opt.Prediction:
            self.__converter = CTCLabelConverter(self.__opt.character)
        else:
            self.__converter = AttnLabelConverter(self.__opt.character)
        
        self.__opt.num_class = len(self.__converter.character)
        
        self.__input_channel_config()
    
    def __input_channel_config(self):
        if self.__opt.rgb:
            self.__opt.input_channel = 3
            
    def get_opt(self):
        return self.__opt
    
    def get_converter(self):
        return self.__converter
    
    def set_model_prediction(self):
        if self.__opt.new_prediction:
            self.__model.Prediction = nn.Linear(self.__model.SequenceModeling_output, len(pretrained_dict['module.Prediction.weight']))  
    
    def model_load_state_dict(self, pretrained_dict):
        if self.__opt.FT:
            self.__model.load_state_dict(pretrained_dict, strict=False)
        else:
            self.__model.load_state_dict(pretrained_dict)
            
    def set_init_constant(self, param):
        if 'bias' in name:
            init.constant_(param, 0.0)
        elif 'weight' in name:
            init.kaiming_normal_(param)
            
    def __load_pre_trained_model(self):
        if self.__opt.saved_model != '':
            pretrained_dict = torch.load(self.__opt.saved_model)
            self.set_model_prediction()
            self.__model = torch.nn.DataParallel(self.__model).to(device)
            print(f'loading pretrained model from {self.__opt.saved_model}')
            
            self.model_load_state_dict(pretrained_dict)

            if self.__opt.new_prediction:
                self.__model.module.Prediction = nn.Linear(self.__model.module.SequenceModeling_output, self.__opt.num_class)  
                for name, param in self.__model.module.Prediction.named_parameters():
                   self.set_init_constant(param)
                self.__model = self.__model.to(device) 
        else:
            # weight initialization
            for name, param in self.__model.named_parameters():
                if 'localization_fc2' in name:
                    print(f'Skip {name} as it is already initialized')
                    continue
                try:
                    self.set_init_constant(param)
                except Exception as e:  # for batchnorm.
                    if 'weight' in name:
                        param.data.fill_(1)
                    continue
            self.__model = torch.nn.DataParallel(self.__model).to(device)
            
    def load_model(self):
        self.__choose_converter()
        self.__model = Model(self.__opt)
        print('model input parameters', self.__opt.imgH, self.__opt.imgW, self.__opt.num_fiducial, self.__opt.input_channel, self.__opt.output_channel,
            self.__opt.hidden_size, self.__opt.num_class, self.__opt.batch_max_length, self.__opt.Transformation, self.__opt.FeatureExtraction,
            self.__opt.SequenceModeling, self.__opt.Prediction)
        
        self.__load_pre_trained_model()
        
        self.train()
        
        return self.__model
        
    def train(self):
        self.__model.train()
        print(f"Model: {self.__model}")
        parameter = Parameter(self.__model)
        parameter.count_parameters()
        
class Loss:
    def __init__(self, opt):
        self.__opt = opt
        
    def set_criterion(self):
        if 'CTC' in self.__opt.Prediction:
            criterion = torch.nn.CTCLoss(zero_infinity=True).to(device)
        else:
            criterion = torch.nn.CrossEntropyLoss(ignore_index=0).to(device)  # ignore [GO] token = ignore index 0
        return criterion
    
    def get_loss(self):
        loss_avg = Averager()
        return loss_avg
        

class Optimizer:
    def __init__(self, opt, model):
        self.__filtered_parameters = []
        self.__params_num = []
        self.__optimizer = None
        self.__model = model
        self.__opt = opt

    def filter_parameter(self):
        for p in filter(lambda p: p.requires_grad, self.__model.parameters()):
            self.__filtered_parameters.append(p)
            self.__params_num.append(np.prod(p.size()))
        print('Trainable params num : ', sum(self.__params_num))
        
    def set_optimizer(self):
        
        self.filter_parameter()
        
        if self.__opt.optim == 'adam':
            self.__optimizer = optim.Adam(self.__filtered_parameters)
        else:
            self.__optimizer = optim.Adadelta(self.__filtered_parameters, lr=self.__opt.lr, rho=self.__opt.rho, eps=self.__opt.eps)
        
        print(f"Optimizer: {self.__optimizer}")
        
        
    def get_optimizer(self):
        
        self.set_optimizer()
        
        return self.__optimizer
    
class LayerControl:
    def __init__(self, opt):
        self.__opt = opt
        
    def freeze_layer(self, model):# freeze some layers
        try:
            if self.__opt.freeze_FeatureFxtraction:
                for param in model.module.FeatureExtraction.parameters():
                    param.requires_grad = False
                    
            if self.__opt.freeze_SequenceModeling:
                for param in model.module.SequenceModeling.parameters():
                    param.requires_grad = False
        except:
            pass       
        
class Trainer:
    def __init__(self, opt):
        self.__opt = opt
        self.__model = None
        self.__num_iter = 0
        self.__best_accuracy = -1
        self.__best_norm_ED = -1
        self.__scaler = GradScaler()
        self.__converter = None
        self.__preds = None
        self.__labels = None
        self.loss_avg = None
        
    def start_training(self, show_number = 2, amp = False):
        valid_dataset_processor = ValidDatasetProcessor(self.__opt)
        valid_loader = valid_dataset_processor.create_valid_dataset()
        model_config = ModelConfiguration(self.__opt)
        self.__model = model_config.load_model()
        self.__converter = model_config.get_converter()
        loss = Loss(self.__opt)
        criterion = loss.set_criterion()
        self.loss_avg = loss.get_loss()
        layer_control = LayerControl(self.__opt)
        layer_control.freeze_layer(self.__model)
        start_time = time.time()
        t1 = time.time()
        validation_log = ValidationLog(self.__opt)
        while(True):
            
            # train part
            # load optimizer
            optimizer_obj = Optimizer(self.__opt, self.__model)
            optimizer = optimizer_obj.get_optimizer()
            optimizer.zero_grad(set_to_none = True)
            
            if amp:
                with autocast():
                    cost = self.__predict(criterion)
                self.__mix_precision_training(cost, optimizer)
            else:
                cost = self.__predict(criterion)
                self.__single_precision_training(cost, optimizer)
            self.loss_avg.add(cost)
            
            i = self.__num_iter
            validationer = Validationer(self.__opt, self.__model)    

            if (i % self.opt.valInterval == 0) and (i!=0):
                print('training time: ', time.time() - t1)
                t1=time.time()
                elapsed_time = time.time() - start_time  
                            
                model.eval()
                
                with torch.no_grad():
                    valid_loss, current_accuracy, current_norm_ED, self.__preds, confidence_score, self.__labels,\
                    infer_time, length_of_data = validation(self.__model, criterion, valid_loader, self.__converter, self.__opt, device)
                
                model.train()
                
                # training loss and validation loss
                loss_log = f'[{i}/{self.__opt.num_iter}] Train loss: {self.loss_avg.val():0.5f}, Valid loss: {valid_loss:0.5f}, Elapsed_time: {elapsed_time:0.5f}'
                self.loss_avg.reset()
                
                current_model_log = f'{"Current_accuracy":17s}: {current_accuracy:0.3f}, {"Current_norm_ED":17s}: {current_norm_ED:0.4f}'
                
                self.keep_best_accuracy_model(current_accuracy, current_norm_ED)
                best_model_log = f'{"Best_accuracy":17s}: {self.__best_accuracy:0.3f}, {"Best_norm_ED":17s}: {self.__best_norm_ED:0.4f}'
                loss_model_log = f'{loss_log}\n{current_model_log}\n{best_model_log}'
                print(loss_model_log)
                
                # show some predicted results
                dashed_line = '-' * 80
                head = f'{"Ground Truth":25s} | {"Prediction":25s} | Confidence Score & T/F'
                predicted_result_log = f'{dashed_line}\n{head}\n{dashed_line}\n'
                            
                start = random.randint(0,len(self.__labels) - show_number )    
                for gt, pred, confidence in zip(self.__labels[start:start+show_number], self.__preds[start:start+show_number], confidence_score[start:start+show_number]):
                    if 'Attn' in opt.Prediction:
                        gt = gt[:gt.find('[s]')]
                        pred = pred[:pred.find('[s]')]

                    predicted_result_log += f'{gt:25s} | {pred:25s} | {confidence:0.4f}\t{str(pred == gt)}\n'
                predicted_result_log += f'{dashed_line}'
                print(predicted_result_log)
                log.write(predicted_result_log + '\n')
                print('validation time: ', time.time()-t1)
                t1=time.time()
                
                validation_log.write_log(loss_model_log, predicted_result_log)
                
            # save model per 1e+4 iter.
            if (i + 1) % 1e+4 == 0:
                torch.save(
                    model.state_dict(), f'./saved_models/{opt.experiment_name}/iter_{i+1}.pth')

            if i == opt.num_iter:
                print('end the training')
                sys.exit()
            self.__num_iter += 1
            
            
    def __CTC_in_Prediction(self, image, text, length, criterion):
        self.__preds = model(image, text).log_softmax(2)
        preds_size = torch.IntTensor([self.__preds.size(1)] * batch_size)
        self.__preds = self.__preds.permute(1, 0, 2)
        torch.backends.cudnn.enabled = False
        cost = criterion(self.__preds, text.to(device), preds_size.to(device), length.to(device))
        torch.backends.cudnn.enabled = True
        
    def __CTC_no_in_Prediction(self, image, text, criterion):
        self.__preds = model(image, text[:, :-1])  # align with Attention.forward
        target = text[:, 1:]  # without [GO] Symbol
        cost = criterion(self.__preds.view(-1, self.__preds.shape[-1]), target.contiguous().view(-1))
    
    def __predict(self, criterion):
        # load train dataset
        train_data_obj = TrainDatasetProcessor(self.__opt)
        train_dataset = train_data_obj.load_train_dataset()
        
        image_tensor, self.__labels = train_dataset.get_batch()
        image = image_tensors.to(device)
        
        text, length = self.__converter.encode(self.__labels, batch_max_length=self.__opt.batch_max_length)
        batch_size = image.size(0)
        
        if 'CTC' in self.__opt.Prediction:
            self.__CTC_in_Prediction(image, text, length, criterion)
        else:
            self.__CTC_no_in_Prediction(image, text, criterion)
        return cost
    
    def __mix_precision_training(self, cost, optimizer):
        scaler.scale(cost).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(self.__model.parameters(), self.__opt.grad_clip)
        scaler.step(optimizer)
        scaler.update()
        
    def __single_precision_training(self, cost, optimizer):
        cost.backward()
        torch.nn.utils.clip_grad_norm_(self.__model.parameters(), self.__opt.grad_clip) 
        optimizer.step()
    
    # keep best accuracy model (on valid dataset)
    def keep_best_accuracy_model(self, current_accuracy, current_norm_ED):
        if current_accuracy > self.__best_accuracy:
            update_best_accuracy(current_accuracy)
        if current_norm_ED > self.__best_norm_ED:
            update_best_norm_ED(current_norm_ED)
            
    def update_best_accuracy(self, current_accuracy):
        self.__best_accuracy = current_accuracy
        torch.save(self.__model.state_dict(), f'./saved_models/{self.__opt.experiment_name}/best_accuracy.pth')
        
    def update_best_norm_ED(self, current_norm_ED):
        self.__best_norm_ED = current_norm_ED
        torch.save(self.__model.state_dict(), f'./saved_models/{self.__opt.experiment_name}/best_norm_ED.pth')

        
    