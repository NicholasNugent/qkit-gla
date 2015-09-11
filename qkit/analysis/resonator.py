# MP@KIT 2015
# HR@KIT 2015
#import h5py
import numpy as np
import logging

from qkit.storage import hdf_lib
#from qkit.analysis.circle_fit import resonator_tools_xtras as rtx
from scipy.optimize import leastsq


class Resonator(object):
    '''
    Resonator class for fitting (live or after measurement) amplitude and phase data at multiple functions. The data is stored in .h5-files, having a NeXus compatible organization.
    Required are datasets frequency (/entry/data0/frequency), amplitude (/entry/data0/amplitude), and phase (/entry/data0/phase).
    input:
    hf (HDF5-file, optional): File containing datasets to be fitted

    Possible fits are 'lorentzian', 'skewed lorentzian', 'circle', and 'fano' with each fit taking arguments
    fit_all (boolean, optional): True or False, default: False, fit all entries in the amplitude dataset or only last one
    f_min (float, optional): Lower boundary for fit function
    f_max (float, optional): Upper boundary for fit function

    usage:
        res=Resonator(hf=hdf_lib.Data(path=path))
        res.fit_lorentzian(fit_all=True,f_min=5.667e9,f_max=5.668e9)
        res.fit_fano(fit_all=True)
        res.fit_circle(fit_all=True,f_max=5.668e9)
    '''

    def __init__(self, hf_path=None):
        self._hf = hdf_lib.Data(path=hf_path)

        self._first_circle = True
        self._first_lorentzian = True
        self._first_fano = True
        self._first_skewed_lorentzian = True

        self._prepare()
    """
    def _refresh(self,live = False):
        if live:
            if self._hf:
                self._hf.close()
            self._hf = hdf_lib.Data(path=self._hf_path)
        self._prepare()
    """

    def set_file(self,hf):
        """
        sets hf file
        input:
        hf (HDF5-file)
        """
        self._hf=hf
        self._prepare()

    def close(self):
        self._hf.close()

    def set_x_coord(self,x_co):
        """
        sets x-coordinate for the datasets
        input:
        x_co (string): url of the x-coordinate
        """
        try:
            self._x_co = self._hf.get_dataset(x_co)
        except:
            logging.warning('Unable to open any x_coordinate. Please set manually using \'set_x_coord()\'.')

    def set_y_coord(self,y_co):
        """
        sets y-coordinate for the datasets
        input:
        y_co (string): url of the y-coordinate
        """
        try:
            self._y_co = self._hf.get_dataset(y_co)
        except:
            logging.warning('Unable to open any y_coordinate. Please set manually using \'set_y_coord()\'.')

    def _set_data_range(self, data):
        '''
        cuts the data array to the positions where f>=f_min and f<=f_max in the frequency-array
        the fit functions are fitted only in this area
        the data in the .h5-file is NOT changed
        '''
        if data.ndim == 1:
            return data[(self._frequency >= self._f_min) & (self._frequency <= self._f_max)]
        if data.ndim == 2:
            ret_array=np.empty(shape=(data.shape[0],self._fit_frequency.shape[0]))
            for i,a in enumerate(data):
                ret_array[i]=data[i][(self._frequency >= self._f_min) & (self._frequency <= self._f_max)]
            return ret_array

    def _prepare(self):
        '''
        reads out the file
        '''
        if not self._hf:
            logging.info('No hf file kown yet!')
            return

        # these ds_url should always be present in a resonator measurement
        ds_url_amp = "/entry/data0/amplitude"
        ds_url_pha = "/entry/data0/phase"
        ds_url_freq = "/entry/data0/frequency"

        # these ds_url depend on the measurement and may not exist
        ds_url_power  = "/entry/data0/power"

        self._ds_amp = self._hf.get_dataset(ds_url_amp)
        self._ds_pha = self._hf.get_dataset(ds_url_pha)

        self._amplitude = np.array(self._hf[ds_url_amp],dtype=np.float64)
        self._phase = np.array(self._hf[ds_url_pha],dtype=np.float64)
        self._frequency = np.array(self._hf[ds_url_freq],dtype=np.float64)

        try:
            self._x_co = self._hf.get_dataset(self._ds_amp.x_ds_url)
        except:
            try: 
                self._x_co = self._hf.get_dataset(ds_url_power) # hardcode a std url
            except:
                logging.warning('Unable to open any x_coordinate. Please set manually using \'set_x_coord()\'.')
        try:
            self._y_co = self._hf.get_dataset(self._ds_amp.y_ds_url)
        except:
            try: self._y_co = self._hf.get_dataset(ds_url_freq) # hardcode a std url
            except:
                logging.warning('Unable to open any y_coordinate. Please set manually using \'set_y_coord()\'.')

    def _global_prepare(self,fit_all,f_min,f_max):
        '''
        prepares the data to be fitted:
        fit_all (bool): True or False, fits the whole dataset or only the last entry
        f_min (float): lower boundary
        f_max (float): upper boundary
        '''
        self._fit_all = fit_all

        if f_min:
            self._f_min = f_min
            if not self._f_min in self._frequency:
                self._f_min = np.min(self._frequency)
                logging.warning('f_min not in frequency array. Taking smallest value in frequency array.')
        else:
            self._f_min = np.min(self._frequency)
        if f_max:
            self._f_max = f_max
            if not self._f_max in self._frequency:
                self._f_max = np.max(self._frequency)
                logging.warning('f_max not in frequency array. Taking largest value in frequency array.')
        else:
            self._f_max = np.max(self._frequency)

        '''
        cut the data-arrays with f_min/f_max and fit_all information
        '''
        self._fit_frequency = np.array(self._set_data_range(self._frequency))
        self._fit_amplitude = np.array(self._set_data_range(self._amplitude))
        self._fit_phase = np.array(self._set_data_range(self._phase))

        '''
        fit_amplitude and fit_phase are always 2dim np arrays.
        for 1dim data, shape: (1, # fit frequency points)
        for 2dim data, shape: (# amplitude slices (i.e. power values in scan), # fit frequency points)
        '''
        if not self._fit_all:
            tmp=np.empty((1,self._fit_frequency.shape[1]))
            tmp[0]=self._fit_amplitude[-1]
            self._fit_amplitude=np.empty(tmp.shape)
            self._fit_amplitude[0] = tmp[0]
            tmp[0]=self._fit_phase[-1]
            self._fit_phase=np.empty(tmp.shape)
            self._fit_phase[0] = tmp[0]

        self._frequency_co = self._hf.add_coordinate('frequency',folder='analysis', unit = 'Hz')
        self._frequency_co.add(self._fit_frequency)

    def _get_starting_values(self):
        pass


    def fit_circle(self,fit_all = False, f_min = None, f_max=None):
        '''
        Calls circle fit from resonator_tools_xtras.py and resonator_tools.py in the qkit/analysis folder
        circle fit for amp and pha data in the f_min-f_max frequency range
        fit parameter, errors, and generated amp/pha data are stored in the hdf-file

        input:
        fit_all (bool): True or False, default: False. Whole data or only last "slice" is fitted (optional)
        f_min (float): lower boundary for data to be fitted (optional, default: None, results in min(frequency-array))
        f_max (float): upper boundary for data to be fitted (optional, default: None, results in max(frequency-array))
        '''

        self._global_prepare(fit_all,f_min,f_max)
        if self._first_circle:
            self._prepare_circle()
            self._first_circle = False

        self._get_data_circle()
        for z_data_raw in self._z_data_raw:
            #z_data_raw = self._set_data_range(z_data_raw)
            try:
                delay, amp_norm, alpha, fr, Qr, A2, frcal = rtx.do_calibration(self._fit_frequency, z_data_raw,ignoreslope=True)
                z_data = rtx.do_normalization(self._fit_frequency, z_data_raw,delay,amp_norm,alpha,A2,frcal)
                results = rtx.circlefit(self._fit_frequency,z_data,fr,Qr,refine_results=False,calc_errors=True)

            except:
                err=np.array(['nan' for f in self._fit_frequency])
                self._amp_gen.append(err)
                self._pha_gen.append(err)
                self._real_gen.append(err)
                self._imag_gen.append(err)

                for key in self._results.iterkeys():
                    self._results[str(key)].append(np.nan)

            else:
                z_data_gen = np.array([A2 * (f - frcal) + rtx.S21(f, fr=float(results["fr"]), Qr=float(results["Qr"]), Qc=float(results["absQc"]), phi=float(results["phi0"]), a= amp_norm, alpha= alpha, delay=delay) for f in self._fit_frequency])
                self._amp_gen.append(np.absolute(z_data_gen))
                self._pha_gen.append(np.angle(z_data_gen))
                self._real_gen.append(np.real(z_data_gen))
                self._imag_gen.append(np.imag(z_data_gen))

                for key in self._results.iterkeys():
                    self._results[str(key)].append(float(results[str(key)]))

    def _prepare_circle(self):
        '''
        creates the datasets for the circle fit in the hdf-file
        '''
        self._result_keys = {"Qi_dia_corr":'', "Qi_no_corr":'', "absQc":'', "Qc_dia_corr":'', "Qr":'', "fr":'', "theta0":'', "phi0":'', "phi0_err":'', "Qr_err":'', "absQc_err":'', "fr_err":'', "chi_square":'', "Qi_no_corr_err":'', "Qi_dia_corr_err":''}
        self._results = {}

        self._circ_amp_gen = self._hf.add_value_matrix('circ_amp_gen', folder = 'analysis', x = self._x_co, y = self._frequency_co, unit = 'a.u.')
        self._circ_pha_gen = self._hf.add_value_matrix('circ_pha_gen', folder = 'analysis', x = self._x_co, y = self._frequency_co, unit='rad')
        self._circ_real_gen = self._hf.add_value_matrix('circ_real_gen', folder = 'analysis', x = self._x_co, y = self._frequency_co, unit='')
        self._circ_imag_gen = self._hf.add_value_matrix('circ_imag_gen', folder = 'analysis', x = self._x_co, y = self._frequency_co, unit='')

        for key in self._result_keys.iterkeys():
           self._results[str(key)] = self._hf.add_value_vector('circ_'+str(key), folder = 'analysis', x = self._x_co, unit ='')

        circ_view_amp = self._hf.add_view('circ_amp', x = self._y_co, y = self._ds_amp)
        circ_view_amp.add(x=self._frequency_co, y=self._circ_amp_gen)
        circ_view_pha = self._hf.add_view('circ_pha', x = self._y_co, y = self._ds_pha)
        circ_view_pha.add(x=self._frequency_co, y=self._circ_pha_gen)

    def _get_data_circle(self):
        '''
        calc complex data from amp and pha
        '''
        if not self._fit_all:
            self._z_data_raw = np.empty((1,self._fit_amplitude.shape[1]), dtype=np.complex64)
            self._z_data_raw[0] = np.array(self._fit_amplitude*np.exp(1j*self._fit_phase),dtype=np.complex64)
        if self._fit_all:
            self._z_data_raw = np.empty((self._fit_amplitude.shape), dtype=np.complex64)
            for i,a in enumerate(self._fit_amplitude):
                self._z_data_raw[i] = self._fit_amplitude[i]*np.exp(1j*self._fit_phase[i])

    def fit_lorentzian(self,fit_all = False,f_min=None,f_max=None):
        '''
        lorentzian fit for amp data in the f_min-f_max frequency range
        squared amps are fitted at lorentzian using scipy.leastsq
        fit parameter, chi2, and generated amp are stored in the hdf-file

        input:
        fit_all (bool): True or False, default: False. Whole data or only last "slice" is fitted (optional)
        f_min (float): lower boundary for data to be fitted (optional, default: None, results in min(frequency-array))
        f_max (float): upper boundary for data to be fitted (optional, default: None, results in max(frequency-array))
        '''
        def residuals(p,x,y):
            f0,k,a,offs=p
            err = y-(a/(1+4*((x-f0)/k)**2)+offs)
            return err

        self._global_prepare(fit_all,f_min,f_max)
        if self._first_lorentzian:
            self._prepare_lorentzian()
            self._first_lorentzian=False
        for amplitudes in self._fit_amplitude:
            amplitudes = np.absolute(amplitudes)
            amplitudes_sq = amplitudes**2

            '''extract starting parameter for lorentzian from data'''
            s_offs = np.mean(np.array([amplitudes_sq[:int(np.size(amplitudes_sq)*.1)], amplitudes_sq[int(np.size(amplitudes_sq)-int(np.size(amplitudes_sq)*.1)):]]))
            '''offset is calculated from the first and last 10% of the data to improve fitting on tight windows'''

            if np.abs(np.max(amplitudes_sq)-np.mean(amplitudes_sq)) > np.abs(np.min(amplitudes_sq)-np.mean(amplitudes_sq)):
                '''peak is expected'''
                s_a = np.abs((np.max(amplitudes_sq)-np.mean(amplitudes_sq)))
                s_f0 = self._fit_frequency[np.argmax(amplitudes_sq)]
            else:
                '''dip is expected'''
                s_a = -np.abs((np.min(amplitudes_sq)-np.mean(amplitudes_sq)))
                s_f0 = self._fit_frequency[np.argmin(amplitudes_sq)]

            '''estimate peak/dip width'''
            mid = s_offs + .5*s_a #estimated mid region between base line and peak/dip
            m = [] #mid points
            for i in range(len(amplitudes_sq)-1):
                if np.sign(amplitudes_sq[i]-mid) != np.sign(amplitudes_sq[i+1]-mid):#mid level crossing
                    m.append(i)
            if len(m)>1:
                s_k = self._fit_frequency[m[-1]]-self._fit_frequency[m[0]]
            else:
                s_k = .15*(self._fit_frequency[-1]-self._fit_frequency[0]) #try 15% of window
            p0=[s_f0, s_k, s_a, s_offs]
            try:
                fit = leastsq(residuals,p0,args=(self._fit_frequency,amplitudes_sq))
            except:
                self._lrnz_amp_gen.append(np.array([np.nan for f in self._fit_frequency]))
                self._lrnz_f0.append(np.nan)
                self._lrnz_k.append(np.nan)
                self._lrnz_a.append(np.nan)
                self._lrnz_offs.append(np.nan)
                self._lrnz_Ql.append(np.nan)
                self._lrnz_chi2_fit.append(np.nan)
            else:
                popt=fit[0]
                chi2 = self._lorentzian_fit_chi2(popt,amplitudes_sq)
                self._lrnz_amp_gen.append(np.sqrt(np.array(self._lorentzian_from_fit(popt))))
                self._lrnz_f0.append(float(popt[0]))
                self._lrnz_k.append(float(np.fabs(float(popt[1]))))
                self._lrnz_a.append(float(popt[2]))
                self._lrnz_offs.append(float(popt[3]))
                self._lrnz_Ql.append(float(float(popt[0])/np.fabs(float(popt[1]))))
                self._lrnz_chi2_fit.append(float(chi2)) 

    def _prepare_lorentzian(self):
        '''
        creates the datasets for the lorentzian fit in the hdf-file
        '''
        self._lrnz_amp_gen = self._hf.add_value_matrix('lrnz_amp_gen', folder = 'analysis', x = self._x_co, y = self._frequency_co, unit = 'a.u.')
        self._lrnz_f0 = self._hf.add_value_vector('lrnz_f0', folder = 'analysis', x = self._x_co, unit = 'Hz')
        self._lrnz_k = self._hf.add_value_vector('lrnz_k', folder = 'analysis', x = self._x_co, unit = 'Hz')
        self._lrnz_a = self._hf.add_value_vector('lrnz_a', folder = 'analysis', x = self._x_co, unit = '')
        self._lrnz_offs = self._hf.add_value_vector('lrnz_offs', folder = 'analysis', x = self._x_co, unit = '')
        self._lrnz_Ql = self._hf.add_value_vector('lrnz_ql', folder = 'analysis', x = self._x_co, unit = '')

        self._lrnz_chi2_fit  = self._hf.add_value_vector('lrnz_chi2' , folder = 'analysis', x = self._x_co, unit = '')

        lrnz_view = self._hf.add_view("lrnz_fit", x = self._y_co, y = self._ds_amp)
        lrnz_view.add(x=self._frequency_co, y=self._lrnz_amp_gen)

    def _lorentzian_from_fit(self,fit):
        return fit[2] / (1 + (4*((self._fit_frequency-fit[0])/fit[1]) ** 2)) + fit[3]

    def _lorentzian_fit_chi2(self, fit, amplitudes_sq):
        chi2 = np.sum((self._lorentzian_from_fit(fit)-amplitudes_sq)**2) / (len(amplitudes_sq)-len(fit))
        return chi2

    def fit_skewed_lorentzian(self, fit_all = False, f_min=None, f_max=None):
        '''
        skewed lorentzian fit for amp data in the f_min-f_max frequency range
        squared amps are fitted at skewed lorentzian using scipy.leastsq
        fit parameter, chi2, and generated amp are stored in the hdf-file

        input:
        fit_all (bool): True or False, default: False. Whole data or only last "slice" is fitted (optional)
        f_min (float): lower boundary for data to be fitted (optional, default: None, results in min(frequency-array))
        f_max (float): upper boundary for data to be fitted (optional, default: None, results in max(frequency-array))
        '''
        def residuals(p,x,y):
            A2, A4, Qr = p
            err = y -(A1a+A2*(x-fra)+(A3a+A4*(x-fra))/(1.+4.*Qr**2*((x-fra)/fra)**2))
            return err
        def residuals2(p,x,y):
            A1, A2, A3, A4, fr, Qr = p
            err = y -(A1+A2*(x-fr)+(A3+A4*(x-fr))/(1.+4.*Qr**2*((x-fr)/fr)**2))
            return err

        self._global_prepare(fit_all,f_min,f_max)
        if self._first_skewed_lorentzian:
            self._prepare_skewed_lorentzian()
            self._first_skewed_lorentzian = False

        for amplitudes in self._fit_amplitude:
            "fits a skewed lorenzian to reflection amplitudes of a resonator"
            amplitudes = np.absolute(amplitudes)
            amplitudes_sq = amplitudes**2

            A1a = np.minimum(amplitudes_sq[0],amplitudes_sq[-1])
            A3a = -np.max(amplitudes_sq)
            fra = self._fit_frequency[np.argmin(amplitudes_sq)]

            p0 = [0., 0., 1e3]

            try:
                p_final = leastsq(residuals,p0,args=(self._fit_frequency,amplitudes_sq))
                A2a, A4a, Qra = p_final[0]

                p0 = [A1a, A2a , A3a, A4a, fra, Qra]
                p_final = leastsq(residuals2,p0,args=(self._fit_frequency,amplitudes_sq))
                popt=p_final[0]
            except:
                self._skwd_amp_gen.append(np.array([np.nan for f in self._fit_frequency]))
                self._skwd_f0.append(np.nan)
                self._skwd_a1.append(np.nan)
                self._skwd_a2.append(np.nan)
                self._skwd_a3.append(np.nan)
                self._skwd_a4.append(np.nan)
                self._skwd_Qr.append(np.nan)
                self._skwd_chi2_fit.append(np.nan)
            else:
                chi2 = self._skewed_fit_chi2(popt,amplitudes_sq)
                amp_gen = np.sqrt(np.array(self._skewed_from_fit(popt)))

                self._skwd_amp_gen.append(amp_gen)
                self._skwd_f0.append(float(popt[4]))
                self._skwd_a1.append(float(popt[0]))
                self._skwd_a2.append(float(popt[1]))
                self._skwd_a3.append(float(popt[2]))
                self._skwd_a4.append(float(popt[3]))
                self._skwd_Qr.append(float(popt[5]))
                self._skwd_chi2_fit.append(float(chi2))

    def _prepare_skewed_lorentzian(self):
        '''
        creates the datasets for the skewed lorentzian fit in the hdf-file
        '''
        self._skwd_amp_gen = self._hf.add_value_matrix('sklr_amp_gen', folder = 'analysis', x = self._x_co, y = self._frequency_co, unit = 'a.u.')
        self._skwd_f0 = self._hf.add_value_vector('sklr_f0', folder = 'analysis', x = self._x_co, unit = 'Hz')
        self._skwd_a1 = self._hf.add_value_vector('sklr_a1', folder = 'analysis', x = self._x_co, unit = 'Hz')
        self._skwd_a2 = self._hf.add_value_vector('sklr_a2', folder = 'analysis', x = self._x_co, unit = '')
        self._skwd_a3 = self._hf.add_value_vector('sklr_a3', folder = 'analysis', x = self._x_co, unit = '')
        self._skwd_a4 = self._hf.add_value_vector('sklr_a4', folder = 'analysis', x = self._x_co, unit = '')
        self._skwd_Qr = self._hf.add_value_vector('sklr_qr', folder = 'analysis', x = self._x_co, unit = '')

        self._skwd_chi2_fit  = self._hf.add_value_vector('sklr_chi2' , folder = 'analysis', x = self._x_co, unit = '')

        skwd_view = self._hf.add_view('sklr_fit', x = self._y_co, y = self._ds_amp)
        skwd_view.add(x=self._frequency_co, y=self._skwd_amp_gen)

    def _skewed_fit_chi2(self, fit, amplitudes_sq):
        chi2 = np.sum((self._skewed_from_fit(fit)-amplitudes_sq)**2) / (len(amplitudes_sq)-len(fit))
        return chi2

    def _skewed_from_fit(self,p):
        A1, A2, A3, A4, fr, Qr = p
        return A1+A2*(self._fit_frequency-fr)+(A3+A4*(self._fit_frequency-fr))/(1.+4.*Qr**2*((self._fit_frequency-fr)/fr)**2)


    def _prepare_fano(self):
        "create the datasets for the fano fit in the hdf-file"

        self._fano_amp_gen = self._hf.add_value_matrix('fano_amp_gen', folder = 'analysis', x = self._x_co, y = self._frequency_co, unit = 'a.u.')
        self._fano_q_fit  = self._hf.add_value_vector('fano_q' , folder = 'analysis', x = self._x_co, unit = '')
        self._fano_bw_fit = self._hf.add_value_vector('fano_bw', folder = 'analysis', x = self._x_co, unit = 'Hz')
        self._fano_fr_fit = self._hf.add_value_vector('fano_fr', folder = 'analysis', x = self._x_co, unit = 'Hz')
        self._fano_a_fit  = self._hf.add_value_vector('fano_a' , folder = 'analysis', x = self._x_co, unit = '')

        self._fano_chi2_fit  = self._hf.add_value_vector('fano_chi2' , folder = 'analysis', x = self._x_co, unit = '')
        self._fano_Ql_fit    = self._hf.add_value_vector('fano_Ql' , folder = 'analysis', x = self._x_co, unit = '')
        self._fano_Q0_fit    = self._hf.add_value_vector('fano_Q0' , folder = 'analysis', x = self._x_co, unit = '')

        fano_view = self._hf.add_view('fano_fit', x = self._y_co, y = self._ds_amp)
        fano_view.add(x=self._frequency_co, y=self._fano_amp_gen)

    def fit_fano(self,fit_all = False, f_min=None, f_max=None):
        '''
        fano fit for amp data in the f_min-f_max frequency range
        squared amps are fitted at fano using scipy.leastsq
        fit parameter, chi2, q0, and generated amp are stored in the hdf-file

        input:
        fit_all (bool): True or False, default: False. Whole data or only last "slice" is fitted (optional)
        f_min (float): lower boundary for data to be fitted (optional, default: None, results in min(frequency-array))
        f_max (float): upper boundary for data to be fitted (optional, default: None, results in max(frequency-array))
        '''
        self._global_prepare(fit_all,f_min,f_max)
        if self._first_fano:
            self._prepare_fano()
            self._first_fano = False

        for amplitudes in self._fit_amplitude:
            amplitude_sq = (np.absolute(amplitudes))**2
            try:
                fit = self._do_fit_fano(amplitude_sq)
                amplitudes_gen = self._fano_reflection_from_fit(fit)

                '''calculate the chi2 of fit and data'''
                chi2 = self._fano_fit_chi2(fit, amplitude_sq)

            except:
                self._fano_amp_gen.append(np.array([np.nan for f in self._fit_frequency]))
                self._fano_q_fit.append(np.nan)
                self._fano_bw_fit.append(np.nan)
                self._fano_fr_fit.append(np.nan)
                self._fano_a_fit.append(np.nan)
                self._fano_chi2_fit.append(np.nan)
                self._fano_Ql_fit.append(np.nan)
                self._fano_Q0_fit.append(np.nan)

            else:
                ''' save the fitted data to the hdf_file'''
                self._fano_amp_gen.append(np.sqrt(np.absolute(amplitudes_gen)))
                self._fano_q_fit.append(float(fit[0]))
                self._fano_bw_fit.append(float(fit[1]))
                self._fano_fr_fit.append(float(fit[2]))
                self._fano_a_fit.append(float(fit[3]))
                self._fano_chi2_fit.append(float(chi2))
                self._fano_Ql_fit.append(float(fit[2])/float(fit[1]))
                q0=self._fano_fit_q0(np.sqrt(np.absolute(amplitudes_gen)),float(fit[2]))
                self._fano_Q0_fit.append(q0)

    def _fano_reflection(self,f,q,bw,fr,a=1,b=1):
        """
        evaluates the fano function in reflection at the
        frequency f
        with
        resonator frequency fr
        attenuation a (linear)
        fano-factor q
        bandwidth bw
        """
        return a*(1 - self._fano_transmission(f,q,bw,fr))

    def _fano_transmission(self,f,q,bw,fr,a=1,b=1):
        """
        evaluates the normalized transmission fano function at the
        frequency f
        with
        resonator frequency fr
        attenuation a (linear)
        fano-factor q
        bandwidth bw
        """
        F = 2*(f-fr)/bw
        return ( 1/(1+q**2) * (F+q)**2 / (F**2+1))

    def _do_fit_fano(self, amplitudes_sq):
        # initial guess
        bw = 1e6
        q  = 1 #np.sqrt(1-amplitudes_sq).min()  # 1-Amp_sq = 1-1+q^2  => A_min = q
        fr = self._fit_frequency[np.argmin(amplitudes_sq)]
        a  = amplitudes_sq.max()

        p0 = [q, bw, fr, a]

        def fano_residuals(p,frequency,amplitude_sq):
            q, bw, fr, a = p
            err = amplitude_sq-self._fano_reflection(frequency,q,bw,fr=fr,a=a)
            return err

        p_fit = leastsq(fano_residuals,p0,args=(self._fit_frequency,np.array(amplitudes_sq)))
        #print ("q:%g bw:%g fr:%g a:%g")% (p_fit[0][0],p_fit[0][1],p_fit[0][2],p_fit[0][3])
        return p_fit[0]

    def _fano_reflection_from_fit(self,fit):
        return self._fano_reflection(self._fit_frequency,fit[0],fit[1],fit[2],fit[3])

    def _fano_fit_chi2(self,fit,amplitudes_sq):
        chi2 = np.sum((self._fano_reflection_from_fit(fit)-amplitudes_sq)**2) / (len(amplitudes_sq)-len(fit))
        return chi2

    def _fano_fit_q0(self,amp_gen,fr):
        '''
        calculates q0 from 3dB bandwidth above minimum in fit function
        '''
        amp_3dB=10*np.log10((np.min(amp_gen)))+3
        amp_3dB_lin=10**(amp_3dB/10)
        f_3dB=[]
        for i in range(len(amp_gen)-1):
            if np.sign(amp_gen[i]-amp_3dB_lin) != np.sign(amp_gen[i+1]-amp_3dB_lin):#crossing@amp_3dB
                f_3dB.append(self._fit_frequency[i])
        if len(f_3dB)>1:
            q0 = fr/(f_3dB[1]-f_3dB[0])
            return float(q0)
        else: return np.nan

    def fit_all_fits(self,fit_all=False,f_min=None,f_max=None):
        self.fit_lorentzian(fit_all,f_min,f_max)
        self.fit_skewed_lorentzian(fit_all,f_min,f_max)
        self.fit_circle(fit_all,f_min,f_max)
        self.fit_fano(fit_all,f_min,f_max)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="resonator.py hdf-based simple resonator fit frontend / KIT 2015")

    parser.add_argument('-f','--file',     type=str, help='hdf filename to open')
    parser.add_argument('-lf','--lorentz-fit',  default=False,action='store_true', help='(optional) lorentzian fit')
    parser.add_argument('-ff','--fano-fit',     default=False,action='store_true', help='(optional) fano fit')
    parser.add_argument('-cf','--circle-fit',   default=False,action='store_true', help='(optional) circle fit')
    parser.add_argument('-slf','--skewed-lorentz-fit', default=False,action='store_true',help='(optional) skewed lorentzian fit')
    parser.add_argument('-all','--fit-all', default=False,action='store_true',help='(optional) fit all entries in dataset')
    parser.add_argument('-fr','--frequency-range', type=str, help='(optional) frequency range for fitting, comma separated')

    args=parser.parse_args()
    #argsfile=None
    if args.file:
        R = Resonator(args.file)
        fit_all = args.fit_all

        if args.frequency_range:
            freq_range=args.frequency_range.split(',')
            f_min=int(freq_range[0])
            f_max=int(freq_range[1])
        else:
            f_min=None
            f_max=None

        if args.circle_fit:
            R.fit_circle(fit_all=fit_all, fmin=f_min,f_max=f_max)
        if args.lorentzian_fit:
            R.fit_lorentzian(fit_all=fit_all, f_min=f_min,f_max=f_max)
        if args.skewed_lorentzian_fit:
            R.fit_skewed_lorentzian(fit_all=fit_all, f_min=f_min,f_max=f_max)
        if args.fano_fit:
            R.fit_fano(fit_all=fit_all, f_min=f_min,f_max=f_max)
        R.close()
    else:
        print "no file supplied. type -h for help"