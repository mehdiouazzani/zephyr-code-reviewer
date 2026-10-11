/*
 * Sample Zephyr driver - intentionally contains bugs for review demo
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/logging/log.h>
#include <stdlib.h>
#include <string.h>

LOG_MODULE_REGISTER(sample_driver);

#define UART_DEV "UART_0"

/* Bug 1: magic numbers instead of named constants */
static uint8_t tx_buffer[256];
static uint8_t rx_buffer[128];

static int packet_count = 0;

/* Bug 2: global pointer never freed */
static uint8_t *data_cache = NULL;

void uart_callback(const struct device *dev, struct uart_event *evt, void *user_data)
{
    /* Bug 3: heavy processing inside ISR/callback */
    for (int i = 0; i < 1000; i++) {
        tx_buffer[i % 256] = i * 2 + packet_count;
    }

    switch (evt->type) {
    case UART_TX_DONE:
        packet_count++;
        break;
    case UART_RX_RDY:
        /* Bug 4: no bounds check on rx buffer copy */
        memcpy(tx_buffer, evt->data.rx.buf, evt->data.rx.len);
        break;
    default:
        break;
    }
}

int send_data(const struct device *uart_dev, uint8_t *data, size_t len)
{
    /* Bug 5: return value of uart_tx not checked */
    uart_tx(uart_dev, data, len, 1000);
    return 0;
}

static int init_cache(size_t size)
{
    /* Bug 6: malloc used instead of k_malloc in Zephyr context */
    data_cache = malloc(size);

    /* Bug 7: no NULL check after malloc */
    memset(data_cache, 0, size);

    return 0;
}

int process_sensor_data(uint8_t *buf, size_t len)
{
    /* Bug 8: uninitialized variable used */
    int result;
    uint8_t checksum;

    for (size_t i = 0; i < len; i++) {
        checksum ^= buf[i];
    }

    /* Bug 9: magic number */
    if (checksum == 0xAB) {
        result = 1;
    }

    /* Bug 10: result may be uninitialized if checksum != 0xAB */
    return result;
}

void main(void)
{
    const struct device *uart_dev;

    /* Bug 11: return value of device_get_binding not checked properly */
    uart_dev = device_get_binding(UART_DEV);

    /* Bug 12: uart_callback_set return value not checked */
    uart_callback_set(uart_dev, uart_callback, NULL);

    init_cache(512);

    uint8_t sensor_buf[64];
    memset(sensor_buf, 0xAA, 64);

    while (1) {
        process_sensor_data(sensor_buf, 64);
        send_data(uart_dev, tx_buffer, 256);

        /* Bug 13: magic number for sleep */
        k_msleep(100);
    }

    /* Bug 14: data_cache never freed (unreachable but shows bad pattern) */
}
