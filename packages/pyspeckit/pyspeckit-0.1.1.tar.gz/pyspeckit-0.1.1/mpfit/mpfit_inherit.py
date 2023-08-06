import mpfit

class mpfit_mine(mpfit.mpfit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fcn = fcn
        self.parnames = self.parinfo(parinfo, 'parname')
        self.parinfo_in = parinfo

    def print_results(self, **kwargs):
        self.defiter(self.fcn, self.params, self.niter, parinfo=self.parinfo_in,
                dof=self.dof, fnorm=self.fnorm, **kwargs)
