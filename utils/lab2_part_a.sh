#!/bin/bash
sweep(){
  TRAFFIC=$1
  ROUTING=$2
  TOPOLOGY="lab2_mesh8x8"
  echo "Running traffic=$TRAFFIC"
  LC_ALL=C utils/sweep.sh src/booksim runfiles/$TOPOLOGY.cfg "traffic=$TRAFFIC" "routing_function=$ROUTING" > logs/task_a_sweep_"$TRAFFIC"_"$ROUTING"_"$TOPOLOGY".log
}

plot(){
  TRAFFIC=$1
  TOPOLOGY="lab2_mesh8x8"
  python3 utils/read_stats.py \
    logs/task_a_sweep_"$TRAFFIC"_dor_"$TOPOLOGY".log \
    logs/task_a_sweep_"$TRAFFIC"_xy_yx_"$TOPOLOGY".log \
    logs/task_a_sweep_"$TRAFFIC"_romm_"$TOPOLOGY".log \
    logs/task_a_sweep_"$TRAFFIC"_valiant_"$TOPOLOGY".log \
    --plot latency --out plots/task_a_sweep_"$TRAFFIC"_"$TOPOLOGY".png
}

run(){
  TRAFFIC=$1
  ROUTING=$2
  INJECTION_RATE=$3
  TOPOLOGY="lab2_mesh8x8"
  src/booksim runfiles/$TOPOLOGY.cfg routing_function=$ROUTING \
    traffic=$TRAFFIC injection_rate=$INJECTION_RATE \
    sent_flits_out=logs/task_a_link_"$TRAFFIC"_"$INJECTION_RATE"_"$ROUTING"_"$TOPOLOGY".txt
}

link_maps(){
  TRAFFIC=$1
  INJECTION_RATE=$2
  TOPOLOGY="lab2_mesh8x8"
  python3 utils/link_heatmap.py \
    plots/task_a_link_"$TRAFFIC"_"$INJECTION_RATE"_"$TOPOLOGY".png \
    "dor, $TRAFFIC, $INJECTION_RATE" \
    logs/task_a_link_"$TRAFFIC"_"$INJECTION_RATE"_dor_"$TOPOLOGY".txt \
    "xy_yx, $TRAFFIC, $INJECTION_RATE" \
    logs/task_a_link_"$TRAFFIC"_"$INJECTION_RATE"_xy_yx_"$TOPOLOGY".txt \
    "romm, $TRAFFIC, $INJECTION_RATE" \
    logs/task_a_link_"$TRAFFIC"_"$INJECTION_RATE"_romm_"$TOPOLOGY".txt \
    "valiant, $TRAFFIC, $INJECTION_RATE" \
    logs/task_a_link_"$TRAFFIC"_"$INJECTION_RATE"_valiant_"$TOPOLOGY".txt
}

#sweep $1 "dor"     &
#sweep $1 "xy_yx"   &
#sweep $1 "romm"    &
#sweep $1 "valiant" &
#wait
plot $1
INJ=0.15
#run $1 "dor"      $INJ & 
#run $1 "xy_yx"    $INJ &
#run $1 "romm"     $INJ &
#run $1 "valiant"  $INJ &
#wait
link_maps $1 $INJ
