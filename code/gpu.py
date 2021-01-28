import tensorflow as tf
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
for device in gpu_devices:
    tf.config.experimental.set_memory_growth(device, True)

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

