"""
Package for Gaussian Process Optimization
=========================================

This package provides optimization functionality
for hyperparameters of covariance functions
:py:class:`pygp.covar` given. 

"""


# import scipy:
import scipy as SP
import scipy.optimize as OPT
import logging as LG
import pdb

LG.basicConfig(level=LG.INFO)

def param_dict_to_list(dict,skeys=None):
    """convert from param dictionary to list"""
    #sort keys
    RV = SP.concatenate([dict[key].flatten() for key in skeys])
    return RV
    pass

def param_list_to_dict(list,param_struct,skeys):
    """convert from param dictionary to list
    param_struct: structure of parameter array
    """
    RV = []
    i0= 0
    for key in skeys:
        val = param_struct[key]
        shape = SP.array(val) 
        np = shape.prod()
        i1 = i0+np
        params = list[i0:i1].reshape(shape)
        RV.append((key,params))
        i0 = i1
    return dict(RV)


def opt_hyper(gpr,gpr2,hyperparams,hyperparams2,Ifilter=None,Ifilter2=None,maxiter=1000,gradcheck=False,bounds = None,optimizer=OPT.fmin_tnc,*args,**kw_args):
    """
    Optimize hyperparemters of :py:class:`pygp.gp.basic_gp.GP` ``gpr`` starting from given hyperparameters ``hyperparams``.

    **Parameters:**

    gpr : :py:class:`pygp.gp.basic_gp`
        GP regression class
    hyperparams : {'covar':logtheta, ...}
        Dictionary filled with starting hyperparameters
        for optimization. logtheta are the CF hyperparameters.
    Ifilter : [boolean]
        Index vector, indicating which hyperparameters shall
        be optimized. For instance::

            logtheta = [1,2,3]
            Ifilter = [0,1,0]

        means that only the second entry (which equals 2 in
        this example) of logtheta will be optimized
        and the others remain untouched.

    bounds : [[min,max]]
        Array with min and max value that can be attained for any hyperparameter

    maxiter: int
        maximum number of function evaluations
    gradcheck: boolean 
        check gradients comparing the analytical gradients to their approximations
    optimizer: :py:class:`scipy.optimize`
        which scipy optimizer to use? (standard lbfgsb)

    ** argument passed onto LML**

    priors : [:py:class:`pygp.priors`]
        non-default prior, otherwise assume
        first index amplitude, last noise, rest:lengthscales
    """

    def f(x):
        x_ = X0
        x_[Ifilter_x] = x

        x_2 = X02
        x_2[Ifilter_x2] = x
        
        rv =  gpr.LML(param_list_to_dict(x_,param_struct,skeys),*args,**kw_args)
        rv2 =  gpr2.LML(param_list_to_dict(x_2,param_struct2,skeys2),*args,**kw_args)

        if SP.absolute((rv-rv2)/rv).max()>1E-1:
            print "delta!"
            pdb.set_trace()
        
        LG.debug("L("+str(x_)+")=="+str(rv))
        if SP.isnan(rv):
            return 1E6
        return rv
    
    def df(x):
        x_ = X0
        x_[Ifilter_x] = x

        x_2 = X02
        x_2[Ifilter_x2] = x
        rv =  gpr.LMLgrad(param_list_to_dict(x_,param_struct,skeys),*args,**kw_args)
        rv2 =  gpr2.LMLgrad(param_list_to_dict(x_2,param_struct2,skeys2),*args,**kw_args)
        #convert to list
        rvl = param_dict_to_list(rv,skeys)[Ifilter_x]
        rvl2 = param_dict_to_list(rv2,skeys2)[Ifilter_x2]
        LG.debug("dL("+str(x_)+")=="+str(rvl))

        if ((SP.absolute((rvl-rvl2)/rvl)>1E-1) & (SP.absolute(rvl-rvl2)>1E-8)).any():
            print "delta!"
            pdb.set_trace()
       
        if SP.isnan(rvl).any():
            In = SP.isnan(rvl)
            rvl[In] = 1E6
        return rvl

    #0. store parameter structure
    skeys = SP.sort(hyperparams.keys())
    param_struct = dict([(name,hyperparams[name].shape) for name in skeys])

    skeys2 = SP.sort(hyperparams2.keys())
    param_struct2 = dict([(name,hyperparams2[name].shape) for name in skeys2])

    
    #1. convert the dictionaries to parameter lists
    X0 = param_dict_to_list(hyperparams,skeys)
    X02 = param_dict_to_list(hyperparams2,skeys2)
    
    Ifilter_x = SP.array(param_dict_to_list(Ifilter,skeys),dtype='bool')
    Ifilter_x2 = SP.array(param_dict_to_list(Ifilter2,skeys2),dtype='bool')
    
    #2. bounds
    if bounds is not None:
        #go through all hyperparams and build bound array (flattened)
        _b = []
        for key in hyperparams.keys():
            if key in bounds.keys():
                _b.extend(bounds[key])
            else:
                _b.extend([(-SP.inf,+SP.inf)]*hyperparams[key].size)
        bounds = SP.array(_b)
        bounds = bounds[Ifilter_x]
        pass
       
        
    #2. set stating point of optimization, truncate the non-used dimensions
    x  = X0.copy()[Ifilter_x]
        
    LG.info("startparameters for opt:"+str(x))
    
    if gradcheck:
        LG.info("check_grad (pre) (Enter to continue):" + str(OPT.check_grad(f,df,x)))
        raw_input()
    
    LG.info("start optimization")

    #general optimizer interface
    #note: x is a subset of X, indexing the parameters that are optimized over
    #Ifilter_x pickes the subest of X, yielding x
    opt_RV=optimizer(f, x, fprime=df, maxfun=maxiter,messages=False,bounds=bounds)
    opt_x = opt_RV[0]
    
    #relate back to X
    Xopt = X0.copy()
    Xopt[Ifilter_x] = opt_x
    #convert into dictionary
    opt_hyperparams = param_list_to_dict(Xopt,param_struct,skeys)
    #get the log marginal likelihood at the optimum:
    opt_lml = gpr.LML(opt_hyperparams,**kw_args)

    if gradcheck:
        LG.info("check_grad (post) (Enter to continue):" + str(OPT.check_grad(f,df,opt_RV[0])))
        raw_input()

    LG.info("old parameters:")
    LG.info(str(hyperparams))
    LG.info("optimized parameters:")
    LG.info(str(opt_hyperparams))
    LG.info("grad:"+str(df(opt_x)))

    return [opt_hyperparams,opt_lml]
