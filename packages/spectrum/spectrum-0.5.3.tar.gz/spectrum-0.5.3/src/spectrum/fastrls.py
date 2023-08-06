import numpy

def  FASTRLS (X, IP, OMEGA, maxINIT=15):
    """
   This subroutine is the fast RLS sequential adaptive algorithm
 
   Input Parameters:
 
      INIT  - Integer set to 0 whenever the algorithm is to be
              re-initialized; program will set it > 0 after first
              pass
      OMEGA - Real exponential weighting factor ( 0 < Omega <= 1)
      IP    - Integer scalar of filter length
      X     - Complex array of contents of input data shift register
 
   Output Parameters:
 
      PF    - Real scalar of forward linear prediction squared error
      AF    - Complex array of forward linear prediction parameters
      PB    - Real scalar of backward linear prediction squared error
      AB     - Complex array of backward linear prediction parameters
      GAMMA - Real scalar gain factor
      C     - Complex array of gain parameters
 
    Notes:
 
      External arrays X,C must be dimensioned .GE. IP+1 and arrays AF,AB
      must be dimensioned  .GE. IP  in the calling program.    Program
      element C(k+1) corresponds to text element c(k), for k=0 to k=IP.

    .. todo:: test, validation. examples
    """
    assert OMEGA>0 and OMEGA<=1, 'omega must be in ]0,1]'
    #Initialization section             ! Eqs. (9.C.31),(9.C.32),(9.C.33)
    AF = numpy.zeros(IP, dtype=complex)
    AB = numpy.zeros(IP, dtype=complex)
    C = numpy.zeros(IP+1, dtype=complex)

    #init=0 case
    GAMMA = 1.
    PF = X[0].real**2 + X[0].imag**2
    for INIT in range(1, IP+1): 
        if INIT>maxINIT:
            break
        EF = X[0]
        if INIT != 1:
            for K in range(0, INIT):
                EF = EF + AF[K] * X[K+1]
        EPF = EF / GAMMA

        PF = OMEGA * PF
        HOLD = EF.conjugate() / PF
        GAMMA = GAMMA + EF.real * HOLD.real - EF.imag * HOLD.imag
        TEMP = X[INIT]
        AF[INIT-1] = -EF / TEMP
        if INIT != 1:
            for K in range(INIT-1,0,-1):
                C[K] = C[K-1] + HOLD * AF[K-1]
        C[0] = HOLD
        if INIT == IP:
            HOLD=-TEMP/GAMMA                           
            PB = (TEMP.real**2 + TEMP.imag**2)/GAMMA    # Eq. (9.C.31)
            for K in range(1,INIT+1):
                AB[K-1]=HOLD*C[INIT-K]
        
    print 'AF=', AF
    print 'PF=',PF
    print 'AB=', AB
    print 'Pb=', PB

    #i  forward predictor update section
    for i in range(IP+1, maxINIT):
        SAVE=OMEGA*PF
        print '###################### INIT' , i
        print 'PB=',PB
        print 'C=',C
        EF = X[0]
        for K in range(1, IP+1):
            EF = EF + AF[K-1]*X[K]                      # Eq. (9.C.1)
        print '--------EF', EF
        EPF = EF/GAMMA            # Eq. (9.C.16)
        HOLD = EF.conjugate()/SAVE
        PF = SAVE + EPF.real * EF.real + EPF.imag*EF.imag # Eq. (9.C.14)
        #C             Test that PF > 0 could be placed here
        GAMMA = GAMMA + EF.real*HOLD.real - EF.imag*HOLD.imag # Eq. (9.C.28)
        #             Test that 0 < GAMMA < 1 could be placed here
        print 'forward', EPF, HOLD, PF, GAMMA, EF
        for K in range(IP, 0, -1):
            TEMP=C[K-1]
            C[K] = TEMP + HOLD * AF[K-1] #Eq. (9.C.27)
            AF[K-1]=AF[K-1] - EPF * TEMP                    # Eq. (9.C.13)
        print 'AF forward', AF
        C[0]=HOLD
    
        #  Backward predictor update section
        SAVE = OMEGA*PB
        EB = SAVE*C[IP].conjugate()                     # Eq. (9.C.25)
        HOLD=C[IP]
        GAMMA=GAMMA-EB.real*HOLD.real+EB.imag*HOLD.imag  # Eq. (9.C.30)
        #C               Test that 0 < GAMMA < 1 could be placed here
        EPB=EB/GAMMA                              # Eq. (9.C.22)
        PB=SAVE+EPB.real*EB.real+EPB.imag*EB.imag        # Eq. (9.C.20)
        print 'backward', SAVE, EB, HOLD, GAMMA, EPB, PB
        #C               Test that PB > 0 could be placed here
        for K in range(1, IP+1):
            TEMP=C[K-1]-HOLD*AB[IP-K]                   # Eq. (9.C.29)
            C[K-1]=TEMP
            AB[IP-K]=AB[IP-K]-EPB*TEMP                  # Eq. (9.C.19)


    print AF
    print PF
    print AB
    print PB


