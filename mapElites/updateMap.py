import numpy as np
import pandas as pd

def updateMap(replaced, replacement, map, fitness, genes, values, extraMapValues):
    mapIsTuple = isinstance(map, tuple)
    # print("genes")
    # print(genes)
    # print("replaced")
    # print(replaced)
    # print("replacement")
    # print(replacement)
    

    fitness = pd.DataFrame(data=fitness.transpose())
    # print("df_fitness")
    # print(df_fitness)
    # print("fitness")
    # print(fitness)


    mapfit_re = map[0].fitness.reshape(map[0].fitness.shape[0] * map[0].fitness.shape[1], 1, order='F')
    mapfit_re[replaced] = fitness.iloc[0][replacement,np.newaxis] # 2d list
    # print("mapfit_re")
    # print(mapfit_re)
    # print(mapfit_re.shape)
    if (isinstance(map,tuple)):
        if (isinstance(map[0],tuple)):
            map[0][0].fitness = mapfit_re.reshape(map[0][0].fitness.shape[0], map[0][0].fitness.shape[1], order='F')
            r, c = np.shape(map[0][0].fitness)
            # print("map[0][0].fitness")
            # print(map[0][0].fitness)
        else:
            map[0].fitness = mapfit_re.reshape(map[0].fitness.shape[0], map[0].fitness.shape[1], order='F')
            r, c = np.shape(map[0].fitness)
            # print("map[0].fitness")
            # print(map[0].fitness)
    else:
        map.fitness = mapfit_re.reshape(map.fitness.shape[0], map.fitness.shape[1], order='F')
        r, c = np.shape(map.fitness)
        # print("map.fitness")
        # print(map.fitness)
    
    # Assign Fitness
    # for i in zip(replaced,replacement):
    #     map[0].fitness[i[0]] = mapfit_re[i[1]]
    # Assign Genomes
    
    # print("replaced")
    # print(replaced)
    # print("replacement")
    # print(replacement)
    # print("r " + str(r))
    # print("c " + str(c))
    replacedI, replacedJ = np.unravel_index(replaced, shape=(r,c), order='F')
    # print("replacedI")
    # print(replacedI)
    # print("replacedJ")
    # print(replacedJ)
    # print("replacement")
    # print(replacement)
    # print(map[0].genes.shape)

    # print(map[0].genes)



    # TODO: check if necessary
    if (isinstance(map,tuple)):
        if (isinstance(map[0],tuple)):
            for iReplace in range(0,len(replaced)):
                map[0][0].genes[0].iloc[replacedI[iReplace]][replacedJ[iReplace]] = genes.iloc[replacement[iReplace]][0] # needs to be adapted for more than 2 genes
                map[0][0].genes[1].iloc[replacedI[iReplace]][replacedJ[iReplace]] = genes.iloc[replacement[iReplace]][1]

            # Assign Miscellaneaous Map values
            if extraMapValues: # not empty
                for iValues in range(0,len(extraMapValues)):
                    for i in zip(replaced,replacement):
                        exec('map[0][0].'+extraMapValues[iValues]+'[i[0]] = values['+str(iValues)+'][i[1]]')

        else:
            # print("replacedI")
            # print(replacedI)
            # print("replacedJ")
            # print(replacedJ)
            # print("replacement")
            # print(replacement)

            for iReplace in range(0,len(replaced)):
                # print(genes.iloc[replacement[iReplace]][0])
                map[0].genes[0][replacedI[iReplace]][replacedJ[iReplace]] = genes.iloc[replacement[iReplace]][0] # needs to be adapted for more than 2 genes
                # print(genes.iloc[replacement[iReplace]][1])
                map[0].genes[1][replacedI[iReplace]][replacedJ[iReplace]] = genes.iloc[replacement[iReplace]][1]
            
            # Assign Miscellaneaous Map values
            # print("replaced")
            # print(replaced)
            # print("replacement")
            # print(replacement)
            if extraMapValues: # not empty
                for iValues in range(0,len(extraMapValues)):
                    for i in zip(replaced,replacement):
                        exec('map[0].'+extraMapValues[iValues]+'[i[0]] = values['+str(iValues)+'][i[1]]')
            
            # print(map[0].genes)
            # print("map[0].genes[0]")
            # print(map[0].genes[0])
            # print("map[0].genes[1]")
            # print(map[0].genes[1])
            # print("genes.iloc[replacement[0]][0]")
            # print(genes.iloc[replacement[0]][0])
            # print(genes.iloc[replacement[0]][1])
    else:
        for iReplace in range(0,len(replaced)):
            map.genes[0].iloc[replacedI[iReplace]][replacedJ[iReplace]] = genes.iloc[replacement[iReplace]][0] # needs to be adapted for more than 2 genes
            map.genes[1].iloc[replacedI[iReplace]][replacedJ[iReplace]] = genes.iloc[replacement[iReplace]][1]
        
        # Assign Miscellaneaous Map values
        if extraMapValues: # not empty
            for iValues in range(0,len(extraMapValues)):
                for i in zip(replaced,replacement):
                    exec('map.'+extraMapValues[iValues]+'[i[0]] = values['+str(iValues)+'][i[1]]')

    return map