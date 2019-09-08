import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import tf_sentencepiece
import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('tf_embed')

logger.info('Tf embed starting.')
print('Tf embed starting.')

tf_embed_loaded = False

# Graph set up.
g = tf.Graph()
with g.as_default():
  text_input = tf.placeholder(dtype=tf.string, shape=[None])
  embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/1")
  embedded_text = embed(text_input)
  init_op = tf.group([tf.global_variables_initializer(), tf.tables_initializer()])
g.finalize()

# Initialize session.
session = tf.Session(graph=g)
session.run(init_op)

logger.info('Tf embed loaded.')
print('Tf embed loaded.')

tf_embed_loaded = True

def text2vec(text):
    vec = session.run(embedded_text, feed_dict={text_input: [ text ]})
    return vec[0]
