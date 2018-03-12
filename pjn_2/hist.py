import numpy as np
import matplotlib.pyplot as plt


data = [410, 392, 390, 404, 314, 374, 347, 206, 302, 433, 432, 348]

months = ('Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.',
          'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.')

y_pos = np.arange(len(data))

plt.bar(y_pos, data, align='center', alpha=0.5)
plt.xticks(y_pos, months)
plt.xlabel('Month')
plt.ylabel('Quantity of judgments')
plt.title('Quantity of judgments per months in 2008')

plt.show()
