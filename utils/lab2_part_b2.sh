#!/bin/bash
run(){
  TRAFFIC=$1
  ROUTING=$2
  INJECTION_RATE=$3
  TOPOLOGY="lab2_mesh8x8"
  src/booksim runfiles/$TOPOLOGY.cfg routing_function=$ROUTING \
    traffic=$TRAFFIC injection_rate=$INJECTION_RATE \
    > logs/task_b2_"$TRAFFIC"_"$INJECTION_RATE"_"$ROUTING"_"$TOPOLOGY".log
}

INJ=0.3
run "uniform" "dor"  $INJ & 
run "uniform" "rmin" $INJ &
