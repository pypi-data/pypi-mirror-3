#include <string>
#include <vector>
#include <cstdlib>
#include <cstdio>
#include <algorithm>
#include <iostream>
using namespace std;
typedef long long ll;
// Utilities
#define S(N) scanf("%d", &N)
#define SS(N) scanf("%s", N)
#define FOR(A,B,C) for(int A=B;A<C;++A)
#define RFOR(A,B,C) for(int A=B;A>=C;--A)
#define MEM(A,B) memset(A,B,sizeof(A))
#define MAX(A,B) ((A > B) ? A : B)
#define MIN(A,B) ((A < B) ? A : B)
// Extras
#define SORT(A) sort( A.begin(),A.end() )
#define PB(A,B) A.push_back(B);
#define MP(A,B) make_pair(A,B)
// Debugging
bool DBG;
#define debug(args...) dbg(),args
struct dbg { template<typename T> dbg& operator , (const T& v) { if(DBG)
cerr << v << " "; return *this; } ~dbg() { if (DBG) cerr << endl; } };
#define PRN(A, N) FOR(j, 0, N) cout << A[j] << " " ; cout << endl;
#define PRRN(A, M, N) FOR(i, 0, M) { PRN(A[i], N) }
#define PR(A) PRN(A, sizeof(A)/sizeof(A[0]))
#define PRR(A) FOR(i, 0, sizeof(A)/sizeof(A[0])) { PR(A[i]) }

#define MOD 100000007
#define LIM 1000000000

int main (int argc, char *argv[]) {
    DBG = (argc > 1 && *argv[1] != '0'); // Set debug on if required
    int t;
    S(t);
    while (t-- > 0) {
        int n;
        S(n);

        printf("%d\n", n);
    }
    return 0;
}

