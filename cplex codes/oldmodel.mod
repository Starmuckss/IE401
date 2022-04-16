/*********************************************
 * OPL 20.1.0.0 Model
 * Author: HP
 * Creation Date: Apr 16, 2022 at 10:13:04 AM
 *********************************************/
/*********************************************
 * OPL 20.1.0.0 Model
 * Author: HP
 * Creation Date: 2 Nis 2022 at 12:47:14
 *********************************************/
// Sýkýntýlar: 
// Holding costlar ve stockout costlar tamamen sallamasyon, internetten daha gerçekçi bir veri bulmam gerekli

int RawMaterialsNumber = ...;
int timeLimit = ...;
range RM =1..RawMaterialsNumber;
range time = 1..timeLimit;

//int averages[RM] = ...;
int LeadTime[RM] = ...;

float CL[RM] =...;
float CS[RM] =...;
float Demand[RM][time]=...;
int MBS[RM] = ...;
int M = ...;
float startingInv[RM] =...;
float SafetyStock[RM][time]=...; // safety stock is an input


dvar boolean y[RM][time];
dvar float+ P[RM][time];
dvar float+ E[RM][time];
dvar boolean B[RM][time]; 
dvar boolean x[RM][time];


execute{
  	cplex.tilim = 120;
	
}

minimize sum(i in RM,j in time) (CL[i]*E[i][j] + CS[i]*B[i][j]);

subject to
{
  // Initialize inventory
  forall(i in RM) E[i][1] == startingInv[i] ;
  
  // Inventory Constraints
  forall(i in RM, j in 2..(LeadTime[i])) E[i][j] == E[i][j-1] - Demand[i][j-1];
  forall(i in RM, j in (LeadTime[i]+1)..timeLimit) E[i][j] == E[i][j-1] + P[i][j-LeadTime[i]] - Demand[i][j-1];
  
  // Purchase Quantity constraint 
  forall(i in RM,j in time) P[i][j] <= M*y[i][j];
  forall(i in RM,j in time) P[i][j] >= y[i][j] * (MBS[i] + SafetyStock[i][j]); 
  
  // Stockout Constraint
  forall(i in RM,j in time) Demand[i][j] - E[i][j] <= M*(1-x[i][j]);
  forall(i in RM,j in time) 1 - B[i][j] <= M*x[i][j];
   	
  //Reorder Point Constraints: (not implemented yet)
  //forall (i in RM,j in time) 1 - y[i][j] <= M * order[i][j];  // Order 0: Make order 1: Don't make order
  //forall (i in RM,j in time) reorderPoint[i] - E[i][j] <= M*(1-order[i][j]);
 
}

 