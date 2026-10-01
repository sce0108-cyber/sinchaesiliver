/* sample05.c
 * 함정 (탐지기가 "위험 후보"로 잡아내지만, 실제로는 안전한 코드)
 *
 * len 은 unsigned 이고 malloc(len + 1) 형태도 sample01과 똑같다.
 * 그런데 이 코드는 malloc 을 부르기 전에 이미 len 의 범위를 검증했다.
 * 즉 이 함수 자체는 안전하다.
 *
 * 하지만 detector.py 의 STEP 5 로직은
 *   "BinaryOp(+) 안에 unsigned 변수가 있는가"
 * 만 확인하고, "그 변수가 이전에 검증되었는가"는 보지 않는다.
 * 그래서 이 파일은 안전한데도 위험 후보로 잡힌다 (오탐, false positive).
 *
 * 과제 STEP 7 에서 이 파일을 돌려보고,
 * 왜 탐지기가 이걸 걸러내지 못하는지, 어떻게 고쳐야 걸러낼 수 있을지
 * 본인 말로 서술할 것.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LEN 4096

char *build_buffer_validated(unsigned int len, const char *src) {
    if (len > MAX_LEN) {          /* 검증이 이미 있다 */
        return NULL;
    }
    char *buf = malloc(len + 1);  /* AST 만 보면 sample01 과 구분이 안 됨 */
    if (buf == NULL) {
        return NULL;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return buf;
}

int main(void) {
    unsigned int len = 10;
    char *b = build_buffer_validated(len, "0123456789");
    printf("%s\n", b);
    free(b);
    return 0;
}
