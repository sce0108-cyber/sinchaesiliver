/* sample04.c
 * 안전 (탐지되면 안 됨)
 * malloc 크기 계산에 변수가 아니라 상수만 쓰인다.
 * BinaryOp(+) 이긴 하지만 unsigned 변수가 없으므로 탐지되지 않아야 한다.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NAME_LEN 32

char *make_name_buffer(void) {
    char *buf = malloc(NAME_LEN + 1);
    if (buf == NULL) {
        return NULL;
    }
    memset(buf, 0, NAME_LEN + 1);
    return buf;
}

int main(void) {
    char *b = make_name_buffer();
    strcpy(b, "safe");
    printf("%s\n", b);
    free(b);
    return 0;
}
