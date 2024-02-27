#!/usr/bin/env python

import math

class AztecUtils():
    scale = [1.8840658e-9, 1.8840658e-9, 1.8840658e-9, 1.8840658e-9, 1.8840658e-9]
    offset = [0.0, 0.0, 0.0, 0.0, 0.0]
    nranges = 4
    vranges = [
        [[-0.00598426, -0.00535386], [-0.00842463, -0.00598426],
         [-0.0308416, -0.00890709], [-3.89967, -0.0383254]],
        [[0.000864763, 0.00155406], [-0.00297336, 0.000864763],
         [-0.0492320, -0.00297336], [-0.787982, -0.0369758]],
        [[0.000308267, 0.000727230], [-0.00182755, 0.000313239],
         [-0.0213227, -0.00171106], [-2.01743, -0.0213227]],
        [[0.54870, 0.97690], [0.97010, 1.11690], 
         [1.11420, 1.31140], [1.27480, 1.64150]],
        [[0.079767, 0.999614], [0.923142, 1.13935], 
         [1.11732, 1.42013], [1.32412, 1.69812]]
        ];
    ncoeffs = [
        [9, 9, 10, 13],
        [9, 9, 9, 8],
        [8, 8, 9, 14],
        [6, 10, 8, 8],
        [11, 12, 11, 10]
        ];
    coeffs =  [
        [21.0339088, 17.6404362, 5.7764468, 1.0391337, -0.2520009, -0.2429733, 
         -0.0253205, 0.0459192, 0.0442522, 3.6324258, 2.8167598, 1.0669831,  
         0.3805553, 0.1299373, 0.0433304, 0.0165281, 0.0049074, 0.0031192,
         0.5926965, 0.4818377, 0.1456406, 0.0808785, 0.0868706, -0.0362857,  
         0.0522146, -0.0150980, 0.0053047, 0.0034045, -1.0314883, 0.5322569, 
         -0.0032120, 4.2274933, -4.9301186, -0.9728079, 3.7388527, 0.9846749, 
         -3.5020370, -0.9828457, 4.9768615, -3.6674335, 0.9560799],
        [20.4345894, 14.5316973, 4.4158678, 0.8287479, -0.0880194, -0.1249974,
         -0.0278568, 0.0139612, 0.0160485, 4.1533346, 3.1883850, 1.3050172,
         0.5174433, 0.2010309, 0.0798375, 0.0327998, 0.0119792, 0.0059549,
         0.6839993, 0.7898692, 0.0821655, 0.1303589, 0.2190582, -0.1577069,
         0.1951773, -0.0889708, 0.0431468, 0.4811210, -0.0621645, 0.1244251,
         0.0608453, -0.0892577, 0.1209017, -0.0670397, 0.0296648],
        [21.8749905, 15.5932236, 4.3449221, 0.5144590, -0.2268376, -0.1097682,
         0.0066758, 0.0349906, 4.5383663, 3.4626067, 1.2612261, 0.4869648,
         0.1982591, 0.0864614, 0.0285047, 0.0179843, 0.9586196, 0.5286568,
         0.2571176, 0.1603136, 0.0870326, 0.0424110, 0.0390248, 0.0005073,
         0.0208422, 0.1798231, 0.3227075, -0.0024272, -0.0733815, 0.2770165,
         -0.2804197, 0.2509424, -0.0890625, -0.0451957, 0.1582727, -0.1654867,
         0.1299048, -0.0623350, 0.0214122],
        [198.267, -94.7212, -1.70153, -0.446484, -0.147150, -0.0521498,
         63.1088, -42.5447, -0.312974, 1.16086, 0.648757, 0.230616, 0.000100099,
         -0.0573665, -0.0494571, -0.00993570, 15.1403, -5.75181, 1.66312,
         -0.105110, -0.188383, -0.245344, -0.0539626, -0.296751, 6.56292,
         -4.54070, -0.135196, -0.286716, -0.114858, -0.0178349, -0.0217677,
         -0.0409648],
        [287.756797, -194.144823, -3.837903, -1.318325, -.109120, -.393265,
         .146911, -.111192, .028877, -.029286, .015619, 71.818025,
         -53.799888, 1.669931, 2.314228, 1.566635, .723026, -.149503,
         .046876, -.388555, .056889, .116823, .058580, 17.304227,
         -7.894688, .453442, .002243, .158036, -.193093, .155717,
         -.085185, .078550, -.018312, .039255, 7.556358, -5.917261,
         .237238, -.334636, -.058642, -.019929, -.020715, -.014814,
         -.008789, -.008554]
        ];
    h2b2scale = 2.19927e-9;
    h2b2offset = 0.0;
    h2b2a = 3.23;
    h2b2b = 0.45;
    h2b2c = 0.70;

    def opacityOld(self, signal):
        fsig = 0;
        ans = 0;

        # convert to volts
        fsig = signal;
        fsig = fsig * self.h2b2scale;
        fsig = fsig + self.h2b2offset;
        ans = fsig;

        # convert to effective tau
        if (fsig >= 0.7):
            ans = abs(math.sqrt(((fsig-self.h2b2c)/self.h2b2a))-self.h2b2b);
        else:
            ans = -99;
        return(ans);

    def opacity(self, signal):
        fsig = 0;
        ans = 0;

        # convert to volts
        fsig = signal;
        fsig = fsig * self.h2b2scale;
        fsig = fsig + self.h2b2offset;
        ans = fsig;

        # convert to effective tau
        if (fsig >= 0.7):
            ans = (0.993 - 1.2*fsig + 0.36*fsig*fsig);
        else:
            ans = -99
        return(ans)

    def cheby(self, i, x):
        if(i==0):
            return(1.0)
        elif (i==1):
            return(x)
        else:
            return(2.0*x*self.cheby(i-1,x) - self.cheby(i-2,x))

    def calibrate(self, signal, idx):
        ans = 0
        if ((idx < 0) or (idx > 4)):
            return(ans)

        whichrange = -1
        findrange = 0

        #apply scaling
        signal = signal * self.scale[idx]
        signal = signal + self.offset[idx]

        #find vrange
        for j in range(self.nranges):
            if((signal >= self.vranges[idx][j][0]) and (signal <= self.vranges[idx][j][1])):
                whichrange = j;
                break;
            else:
                findrange += self.ncoeffs[idx][j]
        
        # chebychev conversion
        if(whichrange >= 0):
            # define proper input variable for chebychev fit
            r_low = self.vranges[idx][whichrange][0];
            r_high = self.vranges[idx][whichrange][1];
            x_cheb = ((signal-r_low)-(r_high-signal))/(r_high-r_low);
        
            for j in range(self.ncoeffs[idx][whichrange]):
                ans += self.coeffs[idx][findrange+j] * self.cheby(j,x_cheb);

        else:
            ans = -99
    
        return(ans);

    def calgrt1(self, signal):
        return self.calibrate(signal, 0)

    def caldiode2(self, signal):
        return self.calibrate(signal, 3)

