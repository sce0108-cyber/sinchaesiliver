/* sample01.c
 * 취약 (탐지되어야 함)
 * len 이 unsigned 이고 검증 없이 malloc 크기 계산에 쓰인다.
 * len 이 UINT_MAX 이면 len + 1 은 0 이 되어 malloc(0) 이 호출된다.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *build_buffer(unsigned int len, const char *src) {
    char *buf = malloc(len + 1);   /* 검증 없음 */
    if (buf == NULL) {
        return NULL;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return buf;
}

int main(void) {
    unsigned int len = 10;
    char *b = build_buffer(len, "0123456789");
    printf("%s\n", b);
    free(b);
    return 0;
}
