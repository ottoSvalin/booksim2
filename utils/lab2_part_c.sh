#!/bin/bash
sweep(){
  TRAFFIC=$1
  ROUTING=$2
  TOPOLOGY="lab2_mesh8x8"
  echo "Running traffic=$TRAFFIC"
  LC_ALL=C utils/sweep.sh src/booksim runfiles/$TOPOLOGY.cfg "traffic=$TRAFFIC" "routing_function=$ROUTING" > logs/task_c_sweep_"$TRAFFIC"_"$ROUTING"_"$TOPOLOGY".log
}

plot(){
  TRAFFIC=$1
  ROUTING=$2
  TOPOLOGY="lab2_mesh8x8"
  python3 utils/read_stats.py \
    logs/task_c_sweep_"$TRAFFIC"_dor_"$TOPOLOGY".log \
    logs/task_c_sweep_"$TRAFFIC"_rmin_"$TOPOLOGY".log \
    logs/task_c_sweep_"$TRAFFIC"_"$ROUTING"_"$TOPOLOGY".log \
    --plot latency --out plots/task_c_sweep_"$TRAFFIC"_"$ROUTING"_"$TOPOLOGY".png
}

run_flits(){
  TRAFFIC=$1
  ROUTING=$2
  INJECTION_RATE=$3
  TOPOLOGY="lab2_mesh8x8"
  src/booksim runfiles/$TOPOLOGY.cfg routing_function=$ROUTING \
    traffic=$TRAFFIC injection_rate=$INJECTION_RATE \
    sent_flits_out=logs/task_c_link_"$TRAFFIC"_"$INJECTION_RATE"_"$ROUTING"_"$TOPOLOGY".txt
}

run(){
  TRAFFIC=$1
  ROUTING=$2
  INJECTION_RATE=$3
  TOPOLOGY="lab2_mesh8x8"
  src/booksim runfiles/$TOPOLOGY.cfg routing_function=$ROUTING \
    traffic=$TRAFFIC injection_rate=$INJECTION_RATE \
    > logs/task_c_run_"$TRAFFIC"_"$INJECTION_RATE"_"$ROUTING"_"$TOPOLOGY".log
}

link_maps(){
  ROUTING=$1
  TOPOLOGY="lab2_mesh8x8"
  python3 utils/link_heatmap.py \
    plots/task_c_link_"$ROUTING"_"$TOPOLOGY".png \
    "$ROUTING, uniform, 0.15" \
    logs/task_c_link_uniform_0.15_"$ROUTING"_"$TOPOLOGY".txt \
    "$ROUTING, transpose, 0.12" \
    logs/task_c_link_transpose_0.12_"$ROUTING"_"$TOPOLOGY".txt \
    "$ROUTING, tornado, 0.12" \
    logs/task_c_link_tornado_0.12_"$ROUTING"_"$TOPOLOGY".txt \
    "$ROUTING, neighbor, 0.4" \
    logs/task_c_link_neighbor_0.4_"$ROUTING"_"$TOPOLOGY".txt
}

hop_count(){
  TRAFFIC=$1
  ROUTING=$2
  INJECTION_RATE=$3
  TOPOLOGY="lab2_mesh8x8"
  echo "[Hop count check] $ROUTING"
  grep -E -m 1 "Hops average" logs/task_c_run_"$TRAFFIC"_"$INJECTION_RATE"_"$ROUTING"_"$TOPOLOGY".log
}

check_deadlock(){
  TRAFFIC=$1
  ROUTING=$2
  INJECTION_RATE=$3
  TOPOLOGY="lab2_mesh8x8"
  echo "[Deadlock check] $ROUTING"
  grep -E -m 1 "Possible network deadlock" logs/task_c_run_"$TRAFFIC"_"$INJECTION_RATE"_"$ROUTING"_"$TOPOLOGY".log
}
## Check hop count
#run "uniform" "dor" 0.05 &
#run "uniform" $1    0.05 &
#wait
#hop_count "uniform" "dor" 0.05
#hop_count "uniform" $1 0.05
#
##Check deadlock
#run "uniform" $1 0.3
#check_deadlock "uniform" $1 0.3

# Run sweep
#sweep "uniform"   $1 &
#sweep "transpose" $1 &
#sweep "tornado"   $1 &
#sweep "neighbor"  $1 &
#wait
echo "Sweep $1 complete!"

#sweep "uniform"   "dor" &
#sweep "transpose" "dor" &
#sweep "tornado"   "dor" &
#sweep "neighbor"  "dor" &
#wait
echo "Sweep dor complete!"

#sweep "uniform"   "rmin" &
#sweep "transpose" "rmin" &
#sweep "tornado"   "rmin" &
#sweep "neighbor"  "rmin" &
#wait
echo "Sweep rmin complete!"

plot "uniform" $1
plot "transpose" $1
plot "tornado" $1
plot "neighbor" $1

# Run with set injection rate 
#run_flits "uniform"   $1 0.15  & 
#run_flits "transpose" $1 0.12  &
#run_flits "tornado"   $1 0.12  &
#run_flits "neighbor"  $1 0.4   &
#wait
echo "Run $1 complete!"
link_maps  $1
