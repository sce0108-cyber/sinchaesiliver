/* sample03.c
 * 안전 (탐지되면 안 됨)
 * len 이 signed int 이다. 이 탐지기는 "unsigned 변수가 쓰였는가"만 보므로
 * 이 경우는 위험 후보로 잡히지 않는다.
 * (signed 오버플로우도 실제로는 위험할 수 있지만, 이번 탐지기의 탐지 범위 밖이다)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *build_buffer(int len, const char *src) {
    if (len < 0 || len > 4096) {
        return NULL;
    }
    char *buf = malloc(len + 1);
    if (buf == NULL) {
        return NULL;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return buf;
}

int main(void) {
    int len = 10;
    char *b = build_buffer(len, "0123456789");
    printf("%s\n", b);
    free(b);
    return 0;
}
