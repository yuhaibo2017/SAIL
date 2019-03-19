import numpy as np
import pandas as pd

def getValidInds(indPool, testFunction, nDesired):
    def any(df): # any is nonzero - equivalent to MATLAB "any"
        for index, row in df.iterrows():
            if row[0]==True or row[0]==1:
                return True
            else:
                continue
        return False
    # inds = []
    inds = pd.DataFrame(data=[])
    # vals = []
    vals = pd.DataFrame(data=[])
    nMissing = nDesired
    nAttempts = 0

    # print(indPool)
    # print(testFunction)
    # print(nDesired)

    while nMissing > 0:
        # Get Next in Pool to test
        testStart = nAttempts + 1
        # print("nAttempts: " + str(nAttempts))
        testEnd = min(indPool.shape[0], nAttempts+nMissing)
        # print("TestStart: " + str(testStart))
        # print("TestEnd: " + str(testEnd))
        if testStart > testEnd:
            break

        nextInd = pd.DataFrame(data=indPool[testStart-1:testEnd,:])
        # nextInd hat immer gleiche Länge und Inhalt -> durchmischen?
        # print("nextInd")
        # print(nextInd)
        # Test for validity
        result = testFunction(nextInd) # Must return a [nInds x nVals] matrix
        result = pd.DataFrame(data=result[:,np.newaxis])
        # Assign valid solutions
        # validInds = np.where()# any isnan TODO
        # print("result")
        # print(result[:, np.newaxis])
        # result_df = pd.DataFrame(data=result[:, np.newaxis])
        # print("result_df")
        # print(result_df)
        not_isnan = pd.DataFrame(data=~np.isnan(result))
        s = not_isnan.loc[:,0]
        validInds = s.to_numpy().nonzero() # liefert Indizes der validen Einträge
        
        # validInds_test = find(any(logical_not(isnan(result)),2))
        # print(type(validInds))
        # any_value = any(not_isnan)
        # print("any_value")
        # print(any_value)
        # validInds = np.nonzero(~np.isnan(result))
        # print("isnan")
        # print(isnan)

        idx_list = validInds[0] # validInds
        # print("idx_list")
        # print(idx_list)
        validInds = pd.DataFrame(data=idx_list[:,np.newaxis])          #CHECKED validInds 100x1 int
        # print("validInds")                                            # CHECKED result 100x1 True
        # print(validInds)                                              # CHECKED nextInd 100x2 samples
        

        # print("result")
        # print(result)
        # print("validInds vlaue to list")
        # print()
        [unpacked_validInds] = validInds.values.T.tolist()
        # print(unpacked_validInds)
        vals_result = result.loc[unpacked_validInds]

        vals_nextInd = nextInd.loc[unpacked_validInds]


        # print("vals_result")
        # print(vals_result)              #             |
                                        # vals_result V
        vals = vals.append(vals_result)
        # vals = np.concatenate((vals, np.take(result, validInds)), axis=1)
        inds = inds.append(vals_nextInd)
        # inds = np.concatenate((inds, np.take(nextInd, validInds)), axis=0)

        # print("vals")
        # print(vals)

        # print("inds")
        # print(inds)


        # vals_df = pd.DataFrame(data=vals_df)
        # print(vals_df)
        # res_val_df = result_df.loc[idx_list]
        # print(res_val_df)
        # vals_df = vals_df.append(res_val_df)

        # print(vals_df)

        # print(nextInd)
        # nextInd_df = pd.DataFrame(data=nextInd)
        # print(nextInd_df)

        # inds_df = pd.DataFrame(data=inds_df)
        # nextInd_inds_df = nextInd_df.loc[idx_list]
        # inds_df = inds_df.append(nextInd_inds_df)
        # print(inds_df)




        # vals = [[vals], [result[validInds,:]]] # vals_df
        # inds = [[inds], [nextInd[validInds,:]]]

        # Retry
        print(nDesired)                                     # nDesired bleibt bei 100 und ändert sich nicht   -> sollte aber stetig sinken von 100 auf 1 zb 100,99,99,98,97,...
        # print(vals_df.shape[0])                           # vals_df shape 0 sinkt 100,99,0,99,0,1,0000-....
        nMissing = nDesired - vals.shape[0]
        
        nAttempts = nAttempts + nextInd.shape[0]
        # print(nAttempts)

    return inds, vals, nMissing, nAttempts
