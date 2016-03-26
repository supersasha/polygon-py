import cProfile
import polygon

cProfile.run('polygon.main()', sort='tottime')
