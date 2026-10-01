/* sample02.c
 * 취약 (탐지되어야 함)
 * 패킷 페이로드 크기를 헤더에서 읽어와 그대로 malloc 크기 계산에 쓴다.
 * payload_size 가 unsigned 이므로 큰 값이 들어오면 오버플로우가 난다.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    unsigned int payload_size;
    char data[1];
} Packet;

char *unpack(unsigned int payload_size, const char *data) {
    char *out = malloc(payload_size + 1);  /* 검증 없음 */
    if (out == NULL) {
        return NULL;
    }
    memcpy(out, data, payload_size);
    out[payload_size] = '\0';
    return out;
}

int main(void) {
    unsigned int payload_size = 32;
    char *out = unpack(payload_size, "example payload");
    printf("%s\n", out);
    free(out);
    return 0;
}
