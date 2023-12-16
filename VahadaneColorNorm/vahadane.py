import spams
import numpy as np
import cv2
import time
import itertools

# From: https://python.hotexamples.com/site/file?hash=0xdcc60d94e5ad7660f7e9cc49857121557c654ebd26abf37ae6a0f977856fbab2


class vahadane(object):
    
    def __init__(self, STAIN_NUM=2, THRESH=0.9, LAMBDA1=0.01, LAMBDA2=0.01, ITER=100, fast_mode=0, getH_mode=0):
        self.STAIN_NUM = STAIN_NUM
        self.THRESH = THRESH
        self.LAMBDA1 = LAMBDA1
        self.LAMBDA2 = LAMBDA2
        self.ITER = ITER
        self.fast_mode = fast_mode # 0: normal; 1: fast
        self.getH_mode = getH_mode # 0: spams.lasso; 1: pinv;
        self.Wt = np.array(())
        self.WtSortIndex = np.array(())

    def show_config(self):
        print('STAIN_NUM =', self.STAIN_NUM)
        print('THRESH =', self.THRESH)
        print('LAMBDA1 =', self.LAMBDA1)
        print('LAMBDA2 =', self.LAMBDA2)
        print('ITER =', self.ITER)
        print('fast_mode =', self.fast_mode)
        print('getH_mode =', self.getH_mode)


    def getV(self, img):
        I0 = img.reshape((-1,3)).T
        I0[I0==0] = 1
        V0 = np.log(255 / I0)
        img_LAB = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        mask = img_LAB[:, :, 0] / 255 < self.THRESH
        I = img[mask].reshape((-1, 3)).T
        I[I == 0] = 1
        V = np.log(255 / I)
        return V0, V
    
    def setWt(self, Wt):
        self.Wt = Wt
        self.WtSortIndex = np.argsort(Wt, axis=1)
        
    def setHt(self, Ht):
        self.Ht = Ht

    def getW(self, V):

        if np.sum(np.asfortranarray(V)) != 0:
            W = spams.trainDL(np.asfortranarray(V), K=self.STAIN_NUM, lambda1=self.LAMBDA1, 
                              iter=self.ITER, mode=2, modeD=0, posAlpha=True, posD=True, verbose=False)
        else:
            W = 0

        W = W / np.linalg.norm(W, axis=0)[None, :] 
        
        if self.Wt.size == 0:
     
            return W
        else:
            dist_ind = []
            pos = list(itertools.permutations(list(np.arange(0,self.STAIN_NUM))))
            # Sort Ws'vectors to minize the SCE between Wt and Ws
            for ele in pos:
                cW = W[:, ele]
                dist_ind.append( np.sum((self.Wt - cW)**2))
            index_min_order = dist_ind.index(min(dist_ind))
            W = W[:, pos[index_min_order]]   
            return W

    def getH(self, V, W):
        if (self.getH_mode == 0):
            try:
                H = spams.lasso(np.asfortranarray(V), np.asfortranarray(W), mode=2, lambda1=self.LAMBDA2, pos=True, verbose=False).toarray()
            except FloatingPointError as exception:
                try:
                    H = np.linalg.pinv(W).dot(V);
                    H[H<0] = 0
                except:
                    H = 0
                    
        elif (self.getH_mode == 1):
            H = np.linalg.pinv(W).dot(V);
            H[H<0] = 0
        else:
            H = 0
        return H


    def stain_separate(self, img):
        if (self.fast_mode == 0):
            V0, V = self.getV(img)
            W = self.getW(V)
            H = self.getH(V0, W)
        elif (self.fast_mode == 1):
            m = img.shape[0]
            n = img.shape[1]
            grid_size_m = int(m / 5)
            lenm = int(m / 20)
            grid_size_n = int(n / 5)
            lenn = int(n / 20)
            W = np.zeros((81, 3, self.STAIN_NUM)).astype(np.float64)
            for i in range(0, 4):
                for j in range(0, 4):
                    px = (i + 1) * grid_size_m
                    py = (j + 1) * grid_size_n
                    patch = img[px - lenm : px + lenm, py - lenn: py + lenn, :]
                    V0, V = self.getV(patch)
                    W[i*9+j] = self.getW(V)
            W = np.mean(W, axis=0)
            V0, V = self.getV(img)
            H = self.getH(V0, W)
        return W, H


    def SPCN(self, img, Ws, Hs):
        Hs_RM = np.percentile(Hs, 99)
        Ht_RM = np.percentile(self.Ht, 99)
        Hs_norm = Hs * Ht_RM / (Hs_RM + 1e-9)
        Vs_norm = np.dot(self.Wt, Hs_norm)
        Is_norm = 255 * np.exp(-1 * Vs_norm)
        I = Is_norm.T.reshape(img.shape).astype(np.uint8)
        return I
