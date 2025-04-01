; Values at time T
(declare-fun Flag1 (Int) Bool)
(declare-fun Flag2 (Int) Bool)
(declare-fun Lock1 (Int) Bool)
(declare-fun Lock2 (Int) Bool)


(assert
(and
    
    (= (Flag1 0) false)
    (= (Flag2 0) false)
    (= (Lock1 0) false)
    (= (Lock2 0) false)

    
    
); End of AND
); End of ASSERT

(check-sat)
(get-model)