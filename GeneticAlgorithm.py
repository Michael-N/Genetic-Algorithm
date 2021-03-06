#!./bin/python
'''
Code By Michael Sherif Naguib
Liscence: MIT open source
Date: 12/11/18
@University of Tulsa
Description: a small library for a genetic algorithm..
'''

#imports 
import random
import copy

#Weighted choice function based on probability distribution:   Code for this function is from https://scaron.info/blog/python-weighted-choice.html 
#                                                              ALL credit for this function to the author Stéphane Caron 
#       I prefered not to simply use the numpy lib but to see how the solution works... 
def weighted_choice(seq, weights):
    assert len(weights) == len(seq)
    assert abs(1. - sum(weights)) < 1e-6

    x = random.random()
    for i, elmt in enumerate(seq):
        if x <= weights[i]:
            return elmt
        x -= weights[i]
#END of the code by Stéphane Caron 
class GeneticAlgorithm:
    def __init__(self,fitFunc,randGeneFunc,mutationFunc,p=10,g=2,mutationProb=5):
        self.popSize=p
        self.genomeSize=g
        self.randomGeneFunction = randGeneFunc
        self.mutationFunction = mutationFunc
        self.mutationProbability = mutationProb
        self.fitnessFunction = fitFunc
        self.populationTotalFitness = None
        self.population=[]
        self.populationProbabilityDistribution = None
        #Make a fake indiviudal and assign a default fitness of 0 and an empty genome
        fakeIndividual = Individual([])
        fakeIndividual.fitness = 0
        self.mostFitOfAllTime = fakeIndividual
    #Compute the Genetic Algorithm: TODO add stopping condition function
    def main(self,stopFunc,generations=100, logFunc=lambda data: print(str(data))):
        #Initilize generation 0 randomly
        currentGen=0
        self.genInitialPop()
        #self.mutatePop() skipped because the genes are random anyway
        self.evalFitnessPop()
        logFunc({"mostFit":self.mostFitOfAllTime,"generationsComputed":currentGen+1})

        #compute the next generation
        while(currentGen<generations):

            #init storage for the new generation:
            newGeneration = []# to boldly go where no one has gone before... these are the voyages of the star ship Enterprise.. [begin theme music]
            #select parents and cross... and append to the new generations
            while(len(newGeneration)<self.popSize):
                parentsTuple = self.selectTwoFromPop(self.populationTotalFitness)
                childrenTuple = parentsTuple[0].cross(parentsTuple[1])
                newGeneration.append(childrenTuple[0])
                newGeneration.append(childrenTuple[1])
            #set the computed generation to be the current population
            self.population = newGeneration
            #mutate the population
            self.mutatePop()
            #Eval the fitness of the population
            self.evalFitnessPop()
            #log the data
            logFunc({"mostFit":self.mostFitOfAllTime,"generationsComputed":currentGen+1})
            #increment the generations
            currentGen = currentGen + 1
            if(stopFunc(self.mostFitOfAllTime)):
                break
        return self.mostFitOfAllTime        
    #generates the intital population
    def genInitialPop(self):
        #Create the individuals
        for i in range(0,self.popSize):
            newGenome = []
            #create each item in the individual's genome
            for j in range(0,self.genomeSize):
                newGenome.append(self.randomGeneFunction())
            #add the individual to the population
            self.population.append(Individual(newGenome))
    #compute fitness
    def evalFitnessPop(self):
        #sum the fitness of the pop...
        totalFitness = 0
        #least fit index:
        leastFitIndex=0
        #calculate the fitness of all the individuals... and check if it is more fit than the fittest of all time
        for i,eachIndividual in enumerate(self.population):
            eachIndividual.evalFitness(self.fitnessFunction)
            totalFitness  =totalFitness + eachIndividual.fitness#sum fitness
            #fittest of all time? if so keep a copy...
            if eachIndividual.fitness > self.mostFitOfAllTime.fitness:
                self.mostFitOfAllTime = copy.deepcopy(eachIndividual)
            #least fit index...
            if(eachIndividual.fitness < self.population[leastFitIndex].fitness):
                leastFitIndex=i
        #UPDATE!!!!NOTE! replace the least fit individual  or a random with the most fit of all time? which will work better?
        #recalculate the total fitness: remove least fit add most fit
        totalFitness = totalFitness - self.population[leastFitIndex].fitness + self.mostFitOfAllTime.fitness
        self.population[leastFitIndex] = copy.deepcopy(self.mostFitOfAllTime)
        
        
        #assign each their probability of selection and store them in a an object list to make lookup faster...
        self.populationProbabilityDistribution = []#reset the list
        for eachIndividual in self.population:
            eachIndividualProb = eachIndividual.fitness/totalFitness
            eachIndividual.probOfSelection = eachIndividualProb
            self.populationProbabilityDistribution.append(eachIndividualProb)       
    #select two individuals from population based on their probability of selection: Universal stochastic selection... returns a tuple of the two selected
    def selectTwoFromPop(self,sumOfFitness):
        #select the first parent
        parentO = weighted_choice(self.population,self.populationProbabilityDistribution)
        #select a canidate for the second
        parentT = weighted_choice(self.population,self.populationProbabilityDistribution)
        #ensure the same parent is not selected twice...
        while(parentT==parentO):
            parentT = weighted_choice(self.population,self.populationProbabilityDistribution)
        return (parentO,parentT)
    #mutates the population according to a integer represented percentage ex. 5 for 5% 
    def mutatePop(self):
        for eachIndividual in self.population:
            eachIndividual.mutate(self.mutationFunction,self.mutationProbability)
class Individual:
    def __init__(self,genome):
        self.genome = genome
        self.fitness = None
        self.probOfSelection = None
    #tostring method
    def __str__(self):
        strTxt = "---------------------------------------------------------------------------\n"
        strTxt = strTxt + "Genome : {0}\nFitness: {1}".format(str(self.genome),str(self.fitness))
        return strTxt
    #Crosses the genes from two individuals
    def cross(self,otherIndividual):
        #crosspoints... i.e the breakpoints for the sections...
        crossPoint = random.randint(1,len(self.genome))
        #pick randomly to the left or right of the crosspoint:
        r = random.randint(0,1)
        ranges = ([0,crossPoint],[crossPoint,len(self.genome)])#left and right respectivly
        selectedRange = ranges[r]
        #create a copy of the parent to be added to the next generation??
        childO = copy.deepcopy(self)
        childT = copy.deepcopy(otherIndividual)
        #cross withine that range
        for i in range(selectedRange[0],selectedRange[1]):
            tmp = childT.genome[i]
            childT.genome[i] = childO.genome[i]
            childO.genome[i] = tmp
        #Set the fitness of the child to None because it is not known yet
        childO.fitness=None
        childT.fitness=None
        #also reset probOfSelection... bc fitness has not assigned it yet
        childO.probOfSelection=None
        childT.probOfSelection=None
        #return the children...
        return (childO,childT)      
    #modifies the genes of this individual
    def mutate(self,mutationFunc = lambda x:x,prob=5):
        for i in range(0,len(self.genome)):
            doMutate= random.randrange(100) < prob
            if(doMutate):
                self.genome[i] = mutationFunc(self.genome[i])
            continue
    #evauluates the fitness of the individual based upon the function
    def evalFitness(self,fitFunc):
        self.fitness = fitFunc(self.genome)

