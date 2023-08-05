# code to define functions on ipython engines
# for executing parallel parameter scans

# set model attribute values
def setModValue(mod,name,value):
    assert hasattr(mod, name), 'Model does not have an attribute: %s ' % name
    setattr(mod, name, float(value))

# analyze steady states
def Analyze(GenOrder,partition,seqarray,mode,UserOutputList,mod):
    state_species = []
    state_flux = []
    user_output_results = []
    invalid_state_list = []
    invalid_state_list_idx = []
    for i in range(len(partition)):
        pars = partition[i]
        for par in range(len(GenOrder)):
            setModValue(mod,GenOrder[par],pars[par])
        if mode == 'state':
            mod.doState()
        elif mode == 'elasticity':
            mod.doElas()
        elif mode == 'mca':
            mod.doMca()
        elif mode == 'stability':
            mod.doEigenMca()
        mod.User_Function()
        if not mod.__StateOK__:
            invalid_state_list.append(pars)
            invalid_state_list_idx.append(seqarray[i])
        state_species.append(mod.state_species)
        state_flux.append(mod.state_flux)
        user_output_results.append([getattr(mod,res) for res in UserOutputList])
    return state_species, state_flux, user_output_results, invalid_state_list, invalid_state_list_idx
