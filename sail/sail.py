import numpy as np
import pandas as pd

from sail.sobol2indx import sobol2indx
from sail.sobol_lib import i4_sobol_generate
from sail.initialSampling import initialSampling
from sail.createPredictionMap import createPredictionMap
from sail.getValidInds import getValidInds

from gaussianProcess.trainGP import trainGP

from domain.rastrigin.rastrigin_CreateAcqFunc import rastrigin_CreateAcqFunc
from domain.rastrigin.rastrigin_PreciseEvaluate import rastrigin_PreciseEvaluate

from domain.cube.cube_CreateAcqFunc import cube_CreateAcqFunc
from domain.cube.cube_PreciseEvaluate import cube_PreciseEvaluate

from domain.wheelcase.wheelcase_CreateAcqFunc import wheelcase_CreateAcqFunc
# from domain.wheelcase.wheelcase_DummyPreciseEvaluate import wheelcase_DummyPreciseEvaluate
from domain.wheelcase.wheelcase_PreciseEvaluate import wheelcase_PreciseEvaluate

from mapElites.createMap import createMap
from mapElites.nicheCompete import nicheCompete
from mapElites.updateMap import updateMap
from mapElites.mapElites import mapElites

from visualization.viewMap import viewMap

import time
from pprint import pprint


def sail(p,d): # domain and params

    # def scale(value):
    #     # return (value - 0)/(1-0)*(0.2 - (-0.2)) + (-0.2) # DOMAINCHANGE
    #     return (value - 0)/(1-0)*(4-0)+0

    def scale1(value):
        return (value - 0)/(1-0)*(4-0)+0 # DOMAINCHANGE

    def scale2(value):
        return (value - 0)/(1-0)*(0.2-0)+0 # DOMAINCHANGE

    # SOBOL settings (adjust also in initialSampling)
    skip     = 1000
    seq_size = 20000

    def feval(funcName,*args):
        return eval(funcName)(*args)
    # Produce initial samples
    if ~d.loadInitialSamples:
        # print("d")
        # pprint(vars(d))
        # print("p")
        # pprint(vars(p))
        # print("d")
        # print(d)
        # print("p.nInitlasmaples")
        # print(p.nInitialSamples)
        observation, value = initialSampling(d,p.nInitialSamples)
        print("DEBUG1: observation")
        print(observation)
        # print("DEBUG2: value")
        # print(value)
    else:
        np.load(d.initialSampleSource) # e.g. npz-File csv
        randomPick = np.random.permutation(observation.shape[0])[:p.initialSamples] # take only first "initialSamples" values
        observation = observation[randomPick,:] # get rows with indexes from randomPick
        value = value[randomPick,:] # same for value

    nSamples = observation.shape[0]

    # Acquisition loop
    trainingTime = []
    illumTime = []
    peTime = []
    predMap = []

    # print("value")
    # print(value)
    percImproved = pd.DataFrame()
    acqMapRecord = pd.DataFrame()
    confContribution = pd.DataFrame()
    gpModel = []
    while nSamples <= p.nTotalSamples:
        # Create surrogate and acquisition function
        # Surrogate models are created from all evaluated samples, and these
        # models are used to produce acquisition function.
        print('PE ' + str(nSamples) + ' | Training Surrogate Models')
        tstart = time.time() # time calc

        # print("value")
        # print(value)
        # print("value.shape[1]: " + str(value.shape))
        # print("d.gpParams.shape: " + str(np.shape(d.gpParams)))
        for iModel in range(0,value.shape[1]): # TODO: only first case relevant
            # only retrain model parameters every 'p.trainingMod' iterations
            # if (nSamples == p.nInitialSamples or np.remainder(nSamples, p.trainingMod * p.nAdditionalSamples)):
            gpModel.insert(iModel,trainGP(observation, value.loc[:,iModel], d.gpParams[iModel]))
            # print("Model")
            # print(gpModel[iModel])
            # else:
                # gpModel.insert(iModel,trainGP(observation, value.loc[:,iModel], d.gpParams[iModel], functionEvals=0))
                # pass

        # Save found model parameters and update acquisition function
        for iModel in range(0,value.shape[1]):
            gpModelDict = gpModel[iModel].to_dict()
            # print("gModelDict")
            # print(gpModelDict)
            d.gpParams[iModel].dict = gpModelDict
            # d.gpParams[iModel] = gpModel[iModel]
            # d.gpParams[iModel].hyp = gpModel[iModel].hyp # See pyGPs hyp
            # d.gpParams[iModel].k = gpModel[iModel].kernel
            # d.gpParams[iModel].meanfunc = gpModel[iModel].mean
            # d.gpParams[iModel].lik = gpModel[iModel].likelihood


        acqFunction = feval(d.createAcqFunction, gpModel, d)

        # Data Gathering (training Time)
        tEnd = time.time()
        trainingTime.append(tEnd - tstart) # time calc

        # Create intermediate prediction map for analysis
        if ~np.remainder(nSamples, p.data_mapEvalMod) and p.data_mapEval:
            print('PE: ' + str(nSamples) + ' | Illuminating Prediction Map')
            predMap[nSamples], x = createPredictionMap(gpModel, observation, p, d, 'featureRes', p.data_predMapRes, 'nGens', 2*p.nGens)

        # 2. Illuminate Acquisition Map
        # A map is constructed using the evaluated samples which are evaluated
        # with the acquisition function and placed in the map as the initial
        # population. The observed samples are the seed population of the
        # 'acquisition map' which is then created by optimizing the acquisition
        # function with MAP-Elites.
        if nSamples == p.nTotalSamples:
            break # After final model is created no more infill is necessary
        print('PE: ' + str(nSamples) + ' | Illuminating Acquisition Map')
        tstart = time.time()

        # Evaluate observation set with acquisition function
        # print("DEBUG3: observation")
        # print(observation)
        fitness, predValues = acqFunction(observation)
        # print("DEBUG4: fitness")
        # print(fitness)
        # print("DEBUG5: predValues")
        # print(predValues)

        # Place best samples in acquisition map
        obsMap = createMap(d.featureRes, d.dof, d.featureMin, d.featureMax, d.extraMapValues)
        # obsMap contains only nans
        # print("obsMap")
        # print(obsMap[0].genes)
        # print("observation")
        # print(observation)
        # print("fitness")
        # print(fitness)
        # print("DEBUG6: obsMap")
        # print(obsMap)
        # print("d")
        # print(d)
        replaced, replacement, x = nicheCompete(observation, fitness, obsMap, d)
        # print("DEBUG7: replaced")
        # print(replaced)
        # print("DEBUG8: replacement")
        # print(replacement)
        # print("x")
        # print(x)
        obsMap = updateMap(replaced, replacement, obsMap, fitness, observation, predValues, d.extraMapValues)
        # print("DEBUG9: obsMap.genes")
        # print(obsMap[0].genes) # OK
        # exit()

        # Illuminate with MAP-Elites
        # print("acqFunc")
        # print(acqFunction)
        # print("obsMap")
        # print(obsMap)
        # print("p")
        # print(p)
        # print("d")
        # print(d)
        acqMap, percImp, h = mapElites(acqFunction, obsMap, p, d)
        # print("DEBUG10: acqMap")
        # print(acqMap)
        # print("DEBUG11: percImp")
        # print(percImp)
        # print("h")
        # print(h)
        # exit()

        # Workaround for acqMap
        if (isinstance(acqMap,tuple)):
            if (isinstance(acqMap[0], tuple)):
                acqMap = acqMap[0][0]
            else:
                acqMap = acqMap[0]
        # viewMap(acqMap,d)
        percImproved[nSamples] = percImp # ok
        # print("percImproved")
        # print(percImproved)
        percImproved.to_csv('percImproved.csv')

        # Data Gathering (illum Time)
        tEnd = time.time()
        illumTime.append(tEnd - tstart) # time calc
        # print("acqMap")
        # pprint(vars(acqMap))
        acqMapRecord.at[0,nSamples] = acqMap
        # print("acqMap.confidence")
        # print(acqMap.confidence)
        # print("fitness_flattened")
        # print(fitness_flattened)
        # print("acqMap.fitness")
        # print(acqMap.fitness)
        fitness_flattened = acqMap.fitness.flatten('F')

        # DEBUG
        # for i in zip(acqMap.confidence, fitness_flattened):
        #     print(i)
        abs_fitness = [abs(val) for val in fitness_flattened]
        # print((acqMap.confidence * d.varCoef) / abs_fitness)
        confContribution.at[0,nSamples] = np.nanmedian( (acqMap.confidence * d.varCoef) / abs_fitness)
        # print("nanmedian") # works
        # print(np.nanmedian( (acqMap.confidence * d.varCoef) / abs_fitness))
        # print("confContribution")
        # print(confContribution)



        # 3. Select infill Samples
        # The next samples to be tested are chosen from the acquisition map: a
        # sobol sequence is used to evenly sample the map in the feature
        # dimensions. When evaluated solutions don't converge or the chosen bin
        # is empty the next bin in the sobol set is chosen.

        print('PE: ' + str(nSamples) + ' | Evaluating New Samples')
        tstart = time.time()

        # At first iteration initialize sobol sequence for sample selection
        if nSamples == p.nInitialSamples:
            sobSet = i4_sobol_generate(d.nDims,20000,1000).transpose()
            sobSet = pd.DataFrame(data=sobSet)
            sobSet = sobSet.sample(frac=1).reset_index(drop=True)
            sobPoint = 1

            # TODO: ADDED: Scaling
            # sobSet = sobSet.applymap(scale) # for wheelcase: first column (0 - 0.4) second column (0 0.2)
            sobSet[0] = sobSet[0].apply(scale1)
            sobSet[1] = sobSet[1].apply(scale2)


        # Choose new samples and evaluate them for new observations
        nMissing = p.nAdditionalSamples
        newValue = pd.DataFrame()
        newSample = pd.DataFrame()
        indPool = pd.DataFrame()
        while nMissing > 0:
            # Evenly sample solutions from acquisition map
            newSampleRange = list(range(sobPoint-1, sobPoint + p.nAdditionalSamples-1))
            # print("DEBUG12: newSampleRange")
            # print(newSampleRange)
            x, binIndx = sobol2indx(sobSet, newSampleRange, d, acqMap.edges)
            # print("DEBUG13: binIndxAfter")
            # print(binIndx)
            # print("DEBUG14: acqMap.genes")
            # print(acqMap.genes)

            for iGenes in range(0,binIndx.shape[0]):
                for gen in range(len(acqMap.genes)):
                    indPool.at[iGenes,gen] = acqMap.genes[gen].iloc[binIndx.iloc[iGenes,0],binIndx.iloc[iGenes,1]]
                    # indPool.at[iGenes,0] = acqMap.genes[0].iloc[binIndx.iloc[iGenes,0],binIndx.iloc[iGenes,1]]
                    # indPool.at[iGenes,1] = acqMap.genes[1].iloc[binIndx.iloc[iGenes,0],binIndx.iloc[iGenes,1]]

            # print("DEBUG15: indPool")
            # print(indPool)
            # print("DEBUG16: observation")
            # print(observation)

            # for iGenes in range(0,binIndx.shape[0]):
            #     indPool[iGenes,:] = acqMap.genes[binIndx.iloc[iGenes,0], binIndx.iloc[iGenes,1], :]

            # Remove repeats and nans (empty bins)
            # repeats in case of rastrigin: almost impossible?
            ds1 = set([tuple(line) for line in indPool.values])
            ds2 = set([tuple(line) for line in observation.values])
            indPool = pd.DataFrame(data=list(ds1.difference(ds2)))
            indPool.dropna(inplace=True) # ok
            indPool.reset_index(drop=True, inplace=True)
            # print("DEBUG17: indPool after")
            # print(indPool)


            # indPool = np.setdiff1d(indPool,observation) # 'rows','stable' ?
            # indPool = indPool[:] # ~any(isnan(indPool),2)

            # Evaluate enough of these valid solutions to get your initial sample set
            peFunction = lambda x: feval(d.preciseEvaluate, x, d) # returns nan if not converged
            # print("indPool")
            # print(indPool)
            # print("DEBUG18: peFunction")
            # print(peFunction)
            # print("nMissing")
            # print(nMissing)

            foundSample, foundValue, nMissing, x = getValidInds(indPool, peFunction, nMissing)
            # print("DEBUG19: foundSample")
            # print(foundSample)
            # print("newSample")
            # print(newSample)
            # print("foundSample")
            # print(foundSample)
            # newSample = [[newSample], [foundSample]]
            newSample = newSample.append(foundSample, ignore_index=True)
            # print("newSample")
            # print(newSample)
            # print("newValue")
            # print(newValue)
            newValue = newValue.append(foundValue, ignore_index=True)
            # newValue = [[newValue], [foundValue]]
            # print("newValue")
            # print(newValue)

            # Advance sobol sequence
            sobPoint = sobPoint + p.nAdditionalSamples + 1

        # Assign found values
        value = value.append(newValue, ignore_index=True)
        # value = [value, newValue] # cat
        # print("value")
        # print(value)
        observation = observation.append(newSample, ignore_index=True)
        # print("observation335")
        # print(observation)
        # observation = [observation, newSample] # cat
        nSamples = np.shape(observation)[0]

        if len(observation) != len(np.unique(observation, axis=0)):
            print('WARNING: duplicate samples in observation set.')

        tEnd = time.time()
        peTime.append(tEnd - tstart)
        # End Acquisition loop

    class Output:
        def __init__(self, p, d, model, trainTime, illum, petime, percImproved, predMap, acqMap, confContrib, unpack):
            self.p = p
            self.d = d
            self.model = model
            self.trainTime = trainTime
            self.illum = illum
            self.petime = petime
            self.percImproved = percImproved
            self.predMap = predMap
            self.acqMap = acqMap
            self.confContrib = confContrib
            self.unpack = unpack
    # Save relevant Data
    output = Output(p, d, gpModel, trainingTime, illumTime, peTime, percImproved, predMap, acqMapRecord, confContribution, '')
    # pprint(vars(output))
    # viewMap(output.acqMap.at[0,190],d)
    # output.p = p
    # output.d = d
    # output.model = gpModel
    # output.trainTime = trainingTime
    # output.illum = illumTime
    # output.petime = peTime
    # output.percImproved = percImproved
    # output.predMap = predMap
    # output.acqMap = acqMapRecord
    # output.confContrib = confContribution
    # output.unpack = '' # necessary?

    # if p.data.outSave:
    #     pass
        # np.save() # sailRun.npz (example)
    return output
