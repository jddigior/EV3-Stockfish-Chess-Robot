#include "PC_FileIO.c"
#include "EV3Servo-lib-UW.c"

//All in mm
const float Z_DIST = 80;	//Distance gripper has to move downwards
const float SQUARE_DIST = 38;
const float GEAR_RAD = 7.0;
const float BELT_RAD = 19.1;
const float WHEEL_RAD = 27.7;

//Miscellaneous constants
const int COORD_SIZE = 4;
const int CAPTURE_ROW = 9;

//Motor Powers
const int X_POWER = 20;
const int Y_POWER = 20;
const int Z_POWER = 20;
const int APPROACH_POWER = 8;

//Moves the wheels and belt simultaneously
void moveXY(int collumn, int row)
{
	//Calculate the desired angles of rotation
	float initEncRow = nMotorEncoder[motorA];
	float X_ANGLE = row * SQUARE_DIST * 180/(WHEEL_RAD*PI) - initEncRow;
	float initEncCol = nMotorEncoder[motorC];
	float Y_ANGLE = collumn * SQUARE_DIST * 180/(BELT_RAD*PI) - abs(initEncCol);

	//Control each motor power with its respective encoder
	//We acknowledge that A and B could be done with just one encoder,
	//	however this resulted in a noticable decrease in driving straightness
	while (abs(nMotorEncoder[motorA] - initEncRow) < abs(X_ANGLE)
				|| abs(nMotorEncoder[motorB] - initEncRow) < abs(X_ANGLE)
				|| abs(nMotorEncoder[motorC] - initEncCol) < abs(Y_ANGLE))
	{
		if (abs(nMotorEncoder[motorA] - initEncRow) < abs(X_ANGLE))
		{
			//motors are updated with decreasing motor powers 
            //   based on how close they are to the target

			int powA = X_POWER - (X_POWER - APPROACH_POWER) 
                      * abs((nMotorEncoder[motorA] - initEncRow)/(X_ANGLE));
			if (X_ANGLE > 0)
				motor[motorA] = powA;
			else
				motor[motorA] = -powA;
		}
		else
			motor[motorA] = 0;

		if (abs(nMotorEncoder[motorB] - initEncRow) < abs(X_ANGLE))
		{
			int powB = X_POWER - (X_POWER - APPROACH_POWER) 
                      * abs((nMotorEncoder[motorA] - initEncRow)/(X_ANGLE));
			if (X_ANGLE > 0)
				motor[motorB] = powB;
			else
				motor[motorB] = -powB;
		}
		else
			motor[motorB] = 0;

		if (abs(nMotorEncoder[motorC] - initEncCol) < abs(Y_ANGLE))
		{
			int powY = Y_POWER - (Y_POWER - APPROACH_POWER) 
                      * abs((nMotorEncoder[motorC] - initEncCol)/(Y_ANGLE));
			if (Y_ANGLE > 0)
				motor[motorC] = -powY;
			else
				motor[motorC] = powY;
		}
		else
			motor[motorC] = 0;

	}
	motor[motorA] = motor[motorB] = motor[motorC] = 0;
}

// moves therack and pinion up or down
// 1 for down, -1 for up
void moveZ(int dir)
{
	float initEnc = nMotorEncoder[motorD];

	const float Z_ANGLE = Z_DIST * 180/(GEAR_RAD*PI);

	while (abs(nMotorEncoder[motorD] - initEnc) < Z_ANGLE)
	{
		int pow = Z_POWER - (Z_POWER - APPROACH_POWER) 
                 * abs((nMotorEncoder[motorD] - initEnc)/(Z_ANGLE));
		if (dir == 1)
		{
			motor[motorD] = pow;
		}
		else
		{
			motor[motorD] = -2*pow; //account for gravity working against rack
		}

	}

	motor[motorD] = 0;
}

//Lifts the piece directly uder the gripper
void liftPiece()
{
	setGripperPosition(S1, 1, 40);
	moveZ(1);
	wait1Msec(100);

	setGripperPosition(S1, 1, 0);
	wait1Msec(500);
	moveZ(-1);
}

//Drops the piece to the square directly under the gripper
void dropPiece()
{
	moveZ(1);
	wait1Msec(100);

	setGripperPosition(S1, 1, 40);
	wait1Msec(100);
	moveZ(-1);
}

//Moves piece from one square to another
void movePiece(int* moveCoord)
{
	moveXY(moveCoord[0], moveCoord[1]);
	liftPiece();
	moveXY(moveCoord[2], moveCoord[3]);
	dropPiece();
}

//Captures piece then moves
void moveCapture(int* moveCoord, int & captureCount)
{
	// Uses int division and modulus to ensure captured pieces 
    //   arent placed in the same location twice
	int capCoord[COORD_SIZE] = {moveCoord[2], moveCoord[3], 
                captureCount % 8, CAPTURE_ROW + captureCount / 8};

	movePiece(capCoord);
	movePiece(moveCoord);
	captureCount++;
}

//Performs en passant capture
void moveEnPassant(int* moveCoord, int* enpasCoord, int & captureCount)
{
	int capCoord[COORD_SIZE] = {enpasCoord[0], enpasCoord[1], 
                captureCount % 8, CAPTURE_ROW + captureCount / 8};
	movePiece(capCoord);
	movePiece(moveCoord);
	captureCount++;
}

//Performs castling move
void moveCastle(int* moveCoord, int* casCoord)
{
	movePiece(casCoord);
	movePiece(moveCoord);
}

//displays current time elapsed since start of game
void displayTime()
{
	displayBigTextLine(13, "Time %02i:%02i", time1[T1]/1000/60, (time1[T1]/1000) % 60);
	//Padding format taken from:
	//https://www.includehelp.com/c-programs/input-an-integer-value-and-print-with-padding-by-zeros.aspx
}

//Must be used in a fast loop
//Allows the player to manually callibrate the gripper arm to A1 square
void allowCalibration()
{
	if(getButtonPress(buttonUp))
	{
		motor[motorC] = APPROACH_POWER;
		nMotorEncoder[motorC] = 0;
	}
	else if(getButtonPress(buttonDown))
	{
		motor[motorC] = -APPROACH_POWER;
		nMotorEncoder[motorC] = 0;
	}
	else if(getButtonPress(buttonLeft))
	{
		motor[motorA] = motor[motorB] = -APPROACH_POWER;
		nMotorEncoder[motorA] = nMotorEncoder[motorB] = 0;
	}
	else if(getButtonPress(buttonRight))
	{
		motor[motorA] = motor[motorB] = APPROACH_POWER;
		nMotorEncoder[motorA] = nMotorEncoder[motorB] = 0;
	}
	else
		motor[motorA] = motor[motorB] = motor[motorC] = 0;
}

//parses instructions file into number arrays to be read later
void readCoord(TFileHandle & fin, int* coord)
{
	char temp = ' ';
	for(int index = 0; index < COORD_SIZE; index++)
	{
		readCharPC(fin, temp);

		//file follows letter-number coordinate convention (i.e. a1a3)
		//This ensures the correct char is subtracted
		if(index % 2 == 0)
			coord[index] = (int)temp - (int)'a';		
            // https://sentry.io/answers/char-to-int-in-c-and-cpp/
		else
			coord[index] = (int)temp - (int)'1';

        /*
            Used to fix an extremely weird bug where after a new file 
            was inserted the read characters would be converted into two or 
            three digit numbers that were random except for the first digit 
            (which was the desired output)
        */
		if (coord[index] > 100)
			coord[index] = coord[index] / 100;      
		else if (coord[index] > 10)							
			coord[index] = coord[index] / 10;
	}
}


//Checks to see if the current file uploaded is different from the one previous
bool readCoordIsDifferent(int* coord)
{
	bool isDifferent = false;
	int lastCoord[4];

	for(int index = 0; index < COORD_SIZE; index++)
	{
		lastCoord[index] = coord[index]; 
        //Populates the previous coordinates before reading again
	}

	TFileHandle fin;
	bool fileOkay = openReadPC(fin, "MoveInstructions.txt");
	if(!fileOkay)
		displayBigTextLine(5, "File not Opened", 10);

	wait1Msec(50);
	readCoord(fin, coord); //read in the new coord

	closeFilePC(fin);

	//in chess you can never have two consecutive moves starting on the same 
	// square therefore only the first two coords need be checked
	if (coord[0] == lastCoord[0] && coord[1] == lastCoord[1])
		isDifferent = false;
	else
	{
		isDifferent = true;
		//displayString(1, "%i %i %i %i", coord[0], coord[1], 
                        lastCoord[0], lastCoord[1]);
		//for debugging
	}

	return isDifferent;
}

//Read the entire instructions file into memory
void readInstructions(int* moveCoord, int &moveType, int* specialMoveCoord, 
                      int &gameState, bool &hasResigned)
{

	while(!readCoordIsDifferent(moveCoord))
	{
		displayTime();
		allowCalibration();
		if(SensorValue[S3] == 1)
		{
			while(SensorValue[S3] == 1){}
			hasResigned = true;
			return;
			//Leave the function immediately if a resign is sent
		}
	}
	wait1Msec(50);

	TFileHandle fin;
	bool fileOkay = openReadPC(fin, "MoveInstructions.txt");
	if(!fileOkay)
		displayBigTextLine(5, "File not Opened", 10);

	readCoord(fin, moveCoord);

	readIntPC(fin, moveType);

	if (moveType == 2 || moveType == 3) //corresponds to enpassant and castling
		readCoord(fin, specialMoveCoord);
	else
	{
		for(int index = 0; index < COORD_SIZE; index++)
		{
			specialMoveCoord[index] = 0;
			//redundant but zeroed out for debugging
		}
	}

	readIntPC(fin, gameState);

	closeFilePC(fin);
}

//Diplays respective message if game has ended
//No win condition has been coded since it is humanly impossible to beat the chess engine
void displayGameEnd(int gameState)
{
		if (gameState == 1)
	{
		displayBigTextLine(1, "Game over -Loss! ");
		displayBigTextLine(3, "Checkmate! ");
	}
	else if (gameState == 2)
	{
		displayBigTextLine(1, "Game over -Draw! ");
		displayBigTextLine(3, "Stalemate! ");
	}
	else if (gameState == 3)
	{
		displayBigTextLine(1, "Game over -Draw! ");
		displayBigTextLine(3, "Insuf Material! ");
	}
	else if (gameState == 4)
	{
		displayBigTextLine(1, "Game over -Draw! ");
		displayBigTextLine(3, "75 Move Rule! ");
	}
	else if (gameState == 5)
	{
		displayBigTextLine(1, "Game over -Draw! ");
		displayBigTextLine(3, "Fivefold Rep! ");
	}
	else
	{
		displayBigTextLine(1, "Game over -Loss! ");
		displayBigTextLine(3, "Resignation! ");
	}
	displayTime();
}

task main()
{
	int moveCoord[COORD_SIZE] = {0,0,0,0};
	int specialMoveCoord[COORD_SIZE] = {0,0,0,0};

	int captureCount = 0;
	int moveType = 0;
	int gameState = 0;
	bool hasResigned = false;

	//Initial calibration steps
	//Moves gripper down to align with A1 square
	moveZ(1);
	displayTextLine(5, "Place A 1 under arm ");
	displayTextLine(6, "Press enter to continue... ");
	while(!getButtonPress(buttonEnter)){
		allowCalibration();
	}
	while(getButtonPress(buttonEnter)){}

	//lift gripper and waits for pieces to be placed
	moveZ(-1);
	displayTextLine(5, "Place down pieces");
	displayTextLine(6, "Press enter to continue... ");

	while(!getButtonPress(buttonEnter)){}
	while(getButtonPress(buttonEnter)){}

	displayTextLine(5, "Play!");
	displayTextLine(6, "  "); // Clear line 6

	time1[T1] = 0;

	do
	{
	displayTime();
	readInstructions(moveCoord, moveType, specialMoveCoord, gameState, hasResigned);

	//for debugging
	/*
	displayTextLine(9, "%i%i%i%i", moveCoord[0],moveCoord[1],
                    moveCoord[2],moveCoord[3]);
	displayTextLine(10, "%i", moveType);
	displayTextLine(11, "%i%i%i%i", specialMoveCoord[0],specialMoveCoord[1],
                    specialMoveCoord[2],specialMoveCoord[3]);
	displayTextLine(12, "%i", gameState);
	*/

	if(!hasResigned)
	{
		if (moveType == 0)
			movePiece(moveCoord);
		else if (moveType == 1)
			moveCapture(moveCoord, captureCount);
		else if (moveType == 2)
			moveEnPassant(moveCoord, specialMoveCoord, captureCount);
		else
			moveCastle(moveCoord, specialMoveCoord);
	}
	moveXY(0,0); //Reset position back to origin

	} while (gameState == 0 && !hasResigned);

	displayGameEnd(gameState);

	displayBigTextLine(5, "Press any button");
	displayBigTextLine(7, "to shut down");
	while(!getButtonPress(buttonAny) && SensorValue[S3] != 1)
	{
		displayTime();
	}
	while(getButtonPress(buttonAny) || SensorValue[S3] == 1){}
}
