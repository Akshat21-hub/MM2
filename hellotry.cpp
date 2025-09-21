#include <iostream>
#include <vector>
#include <map>
#include <stack>
#include <set>
#include <algorithm>
#include <thread>
#include <chrono>

using namespace std;

struct Point {
    int r, c;
    bool operator<(const Point &other) const {
        return r == other.r ? c < other.c : r < other.r;
    }
    bool operator==(const Point &other) const {
        return r == other.r && c == other.c;
    }
};

// ----- Maze -----
Point start{8,1};
Point end{1,10};

vector<vector<Point>> branches = {
    {{3,5},{3,3},{2,3}}, 
    {{5,5},{5,3},{4,3},{4,4},{5,4}},
    {{4,7},{4,9}}, 
    {{2,7},{2,6},{1,6}},
    {{6,1},{6,3}},
    {{5,7},{7,7},{7,6},{6,6}},
    {{3,1},{3,2},{2,2}},
    {{1,3},{0,3}},
    {{1,5},{0,5}},
    {{6,7},{6,8},{5,8},{4,8}}
};

vector<Point> main_path = {
    {8,1},{7,1},{6,1},{5,1},{4,1},
    {3,1},{2,1},{1,1},{1,2},{1,3},{1,4},{1,5},
    {2,5},{3,5},{4,5},{5,5},{6,5},{6,6},{6,7},
    {5,7},{4,7},{3,7},{2,7},{1,7},{1,8},{1,9},{1,10}
};

// ----- Graph -----
map<Point, vector<Point>> graph;

void add_edge(Point a, Point b){
    graph[a].push_back(b);
    graph[b].push_back(a);
}

void register_path(vector<Point> &path){
    for(size_t i=0;i<path.size()-1;i++){
        add_edge(path[i], path[i+1]);
    }
}

void build_graph(){
    register_path(main_path);
    for(auto &b : branches){
        register_path(b);
    }
}

// ----- DFS Priority (L/S/R/B) -----
int turn_priority(Point prev, Point current, Point neighbor){
    if(prev.r == -1 && prev.c == -1) return 1; // starting node → straight

    int vx = current.c - prev.c;
    int vy = prev.r - current.r; // grid row increases downward
    int nx = neighbor.c - current.c;
    int ny = current.r - neighbor.r;

    int cp = vx*ny - vy*nx;
    int dp = vx*nx + vy*ny;

    if(cp > 0) return 0; // LEFT
    else if(cp < 0) return 2; // RIGHT
    else {
        if(dp > 0) return 1; // STRAIGHT
        else return 3; // BACK
    }
}

Point detect_next_node(Point current, Point prev, set<pair<Point,Point>> &visited_edges){
    vector<Point> neighbors = graph[current];
    vector<Point> candidates;

    for(auto n : neighbors){
        pair<Point,Point> e = n < current ? make_pair(n,current) : make_pair(current,n);
        if(visited_edges.find(e) == visited_edges.end())
            candidates.push_back(n);
    }

    if(candidates.empty())
        return prev; // dead end → backtrack

    sort(candidates.begin(), candidates.end(), [&](Point a, Point b){
        return turn_priority(prev,current,a) < turn_priority(prev,current,b);
    });

    Point next = candidates[0];
    pair<Point,Point> e = next < current ? make_pair(next,current) : make_pair(current,next);
    visited_edges.insert(e);
    return next;
}

// ----- Display -----
void print_maze(Point bot){
    cout << "\033[2J\033[H"; // clear console
    for(int r=0;r<9;r++){
        for(int c=0;c<12;c++){
            Point p{r,c};
            if(p == bot) cout << "B ";
            else if(find(main_path.begin(), main_path.end(), p) != main_path.end()) cout << ". ";
            else {
                bool in_branch = false;
                for(auto &b : branches){
                    if(find(b.begin(),b.end(),p) != b.end()) { in_branch = true; break; }
                }
                cout << (in_branch ? ". " : "# ");
            }
        }
        cout << endl;
    }
}

// ----- Main -----
int main(){
    build_graph();

    stack<pair<Point,Point>> dfs_stack;
    dfs_stack.push({start,{-1,-1}});
    set<pair<Point,Point>> visited_edges;

    Point bot_pos = start;
    print_maze(bot_pos);
    this_thread::sleep_for(chrono::milliseconds(500));

    while(!dfs_stack.empty()){
        auto [node, prev] = dfs_stack.top();

        if(node == end){
            bot_pos = node;
            print_maze(bot_pos);
            cout << "Reached END!" << endl;
            dfs_stack.pop();
            break;
        }

        Point next = detect_next_node(node, prev, visited_edges);

        if(next == prev){ // backtrack
            dfs_stack.pop();
            if(!dfs_stack.empty()) bot_pos = dfs_stack.top().first;
        } else {
            dfs_stack.push({next,node});
            bot_pos = next;
        }

        print_maze(bot_pos);
        cout << "Current Node: (" << node.r << "," << node.c << ")\n";
        cout << "Stack size: " << dfs_stack.size() << endl;
        cout << "Visited edges: " << visited_edges.size() << endl;
        cout << "Press ENTER to continue...";
        cin.get(); // step-by-step pause
    }

    cout << "Simulation complete. Press ENTER to exit." << endl;
    cin.get();
    return 0;
}
