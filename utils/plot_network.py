"""
Plot MSDNetwork
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animate

class PlotMSDNetwork():

    def rtplot(self, table, table_length: int, ylim: tuple, refresh_time: float) -> None:
        
        """
        plot network animation

        table: Generator, function table generator
        ylim: tuple, limit on y axis
        refresh_time: float, refresh time
        """

        fig, ax = plt.subplots(figsize=(15, 10))
        n = table_length
        x = [j for j in range(n)]
        def update(i):
            y = next(table)
            ax.clear()
            ax.set_ylim(ylim)
            ax.plot(x, y)
        animation = animate.FuncAnimation(fig, update, interval=refresh_time)
        plt.show()

