from docplex.mp.model import Model
from docplex.cp.model import CpoModel
import instanceGeneration


class CPLEX:
    def __init__(self, fp_listCplexParameters, fp_obInstance):
        '''
        @fp_listCplexParameters: [0:iCandidateFaciNum, 1:fAlpha]
        '''
        self.iCandidateFaciNum = fp_listCplexParameters[0]
        self.fAlpha = fp_listCplexParameters[1]
        self.obInstance = fp_obInstance
        self.model = Model()
        self.cpomodel = CpoModel()

    def fun_fillModel(self):
        # creat decision variables list
        listDeciVarX = self.model.binary_var_list(self.iCandidateFaciNum, lb=0, name='X')
        listDeciVarY = self.model.binary_var_list(pow(self.iCandidateFaciNum, 3), lb=0, name='Y')
        # construct objective function
        objFunction = 0
        for i in range(self.iCandidateFaciNum):
            objFunction += self.obInstance.aiFixedCost[i] * listDeciVarX[i]
        listTranCost = []
        for i in range(self.iCandidateFaciNum):
            for j in range(self.iCandidateFaciNum):
                for r in range(2):  # 只分配两个设施
                    fTranCost = self.fAlpha * self.obInstance.aiDemands[i] * self.obInstance.af_2d_TransCost[i][j] * pow(self.obInstance.fFaciFailProb, r) * (1 - self.obInstance.fFaciFailProb)
                    listTranCost.append(fTranCost)
                    objFunction += fTranCost * listDeciVarY[pow(self.iCandidateFaciNum, 2) * i + self.iCandidateFaciNum * j + r]
        # for i in range(pow(self.iCandidateFaciNum, 2) * 2):
        #     objFunction += listTranCost[i] * listDeciVarY[i]
        self.model.minimize(objFunction)
        # add constraints
        for i in range(self.iCandidateFaciNum):
            for r in range(2):  # 只分配两个设施
                cons1 = 0
                for j in range(self.iCandidateFaciNum):
                    cons1 += listDeciVarY[i * pow(self.iCandidateFaciNum, 2) + j * self.iCandidateFaciNum + r]
                self.model.add_constraint(cons1 == 1)  # constraint 1

        for i in range(self.iCandidateFaciNum):
            for j in range(self.iCandidateFaciNum):
                cons3 = 0
                for r in range(2):  # 只分配两个设施
                    cons3 += listDeciVarY[i * pow(self.iCandidateFaciNum, 2) + j * self.iCandidateFaciNum + r]
                self.model.add_constraint(cons3 <= listDeciVarX[j])  # constraint 3

        cons4 = 0
        for j in range(self.iCandidateFaciNum):
            cons4 += listDeciVarX[j]
        self.model.add_constraint(cons4 >= 2)

    def fun_fillCpoModel(self):
        # creat decision variables list
        listDeciVarX = self.cpomodel.binary_var_list(self.iCandidateFaciNum, name='X')
        listDeciVarY = self.cpomodel.binary_var_list(pow(self.iCandidateFaciNum, 3), name='Y')
        # construct objective function
        objFunction = 0
        for i in range(self.iCandidateFaciNum):
            objFunction += self.obInstance.aiFixedCost[i] * listDeciVarX[i]
        listTranCost = []
        for i in range(self.iCandidateFaciNum):
            for j in range(self.iCandidateFaciNum):
                for r in range(2):  # 只分配两个设施
                    fTranCost = self.fAlpha * self.obInstance.aiDemands[i] * self.obInstance.af_2d_TransCost[i][j] * pow(self.obInstance.fFaciFailProb, r) * (1 - self.obInstance.fFaciFailProb)
                    listTranCost.append(fTranCost)
                    objFunction += fTranCost * listDeciVarY[pow(self.iCandidateFaciNum, 2) * i + self.iCandidateFaciNum * j + r]
        # for i in range(pow(self.iCandidateFaciNum, 2) * 2):
        #     objFunction += listTranCost[i] * listDeciVarY[i]
        self.cpomodel.add(self.cpomodel.minimize(objFunction))
        # add constraints
        for i in range(self.iCandidateFaciNum):
            for r in range(2):  # 只分配两个设施
                cons1 = 0
                for j in range(self.iCandidateFaciNum):
                    cons1 += listDeciVarY[i * pow(self.iCandidateFaciNum, 2) + j * self.iCandidateFaciNum + r]
                self.cpomodel.add(cons1 == 1)  # constraint 1

        for i in range(self.iCandidateFaciNum):
            for j in range(self.iCandidateFaciNum):
                cons3 = 0
                for r in range(2):  # 只分配两个设施
                    cons3 += listDeciVarY[i * pow(self.iCandidateFaciNum, 2) + j * self.iCandidateFaciNum + r]
                self.cpomodel.add(cons3 <= listDeciVarX[j])  # constraint 3

        cons4 = 0
        for j in range(self.iCandidateFaciNum):
            cons4 += listDeciVarX[j]
        self.cpomodel.add(cons4 >= 2)


if __name__ == '__main__':
    '''
    @listInstPara=[0:iSitesNum, 1:iScenNum, 2:iDemandLB, 3:iDemandUB, 4:iFixedCostLB, 5:iFixedCostUP, 6:iCoordinateLB, 7:iCoordinateUB, 8:fFaciFailProb]

    @fp_listCplexParameters: [0:iCandidateFaciNum, 1:fAlpha]
    '''
    listInstPara = [5, 1, 0, 1000, 100, 1000, 0, 1, 0.05]
    # Generate instance
    obInstance = instanceGeneration.Instances(listInstPara)
    obInstance.funGenerateInstances()
    # cplex
    listCplexParameters = [5, 1]
    cplexSolver = CPLEX(listCplexParameters, obInstance)
    # ------------------------docplex-mp module--------------------
    cplexSolver.fun_fillModel()
    cplexSolver.model.parameters.mip.tolerances.mipgap = 0.0001  # 控制gap/tolerance, 0.1即10%
    sol = cplexSolver.model.solve()
    print("Objective value: ", sol.get_objective_value())
    print(sol.solve_details)  # 获取解的详细信息，如时间，gap值等
    cplexSolver.model.print_information()
    for i in range(cplexSolver.iCandidateFaciNum):
        if sol.get_value('X_'+str(i)) == 1:
            print('X_'+str(i)+" =", 1)
    # print(sol)  # 获取所有的变量解
    # print('-------------------------------------------------------------------')
    # -----------------------docplex-cp module---------------------
    cplexSolver.fun_fillCpoModel()
    cpsol = cplexSolver.cpomodel.solve(RelativeOptimalityTolerance=0.00, TimeLimit=10)
    print("Solution status: " + cpsol.get_solve_status())

    for i in range(cplexSolver.iCandidateFaciNum):
        if cpsol.get_all_var_solutions()[i].get_value() == 1:
            print(cpsol.get_all_var_solutions()[i].get_name() + " =", cpsol.get_all_var_solutions()[i].get_value())  # 打印出Xj==1的决策变量
    # print(cpsol)
    # print(type(sol))