import random

from data.WebNLG.reader import WebNLGDataReader
from data.reader import DataReader, DataSetType
from planner.naive_planner import NaivePlanner
from planner.planner import Planner
from process.evaluation import EvaluationPipeline
from process.pre_process import TrainingPreProcessPipeline, TestingPreProcessPipeline
from process.train_model import TrainModelPipeline
from process.train_planner import TrainPlannerPipeline
from process.translate import TranslatePipeline
from scorer.global_direction import GlobalDirectionExpert
from scorer.product_of_experts import WeightedProductOfExperts
from scorer.relation_direction import RelationDirectionExpert
from scorer.relation_transitions import RelationTransitionsExpert
from scorer.splitting_tendencies import SplittingTendenciesExpert
from utils.pipeline import Pipeline


class Config:
    def __init__(self, reader: DataReader, planner: Planner, test_reader: DataReader = None):
        self.reader = {
            DataSetType.TRAIN: reader,
            DataSetType.DEV: reader,
            DataSetType.TEST: test_reader if test_reader else reader,
        }
        self.planner = planner


MainPipeline = Pipeline()
MainPipeline.enqueue("pre-process", "Pre-process training data", TrainingPreProcessPipeline)
MainPipeline.enqueue("train-planner", "Train Planner", TrainPlannerPipeline)
MainPipeline.enqueue("train-model", "Train Model", TrainModelPipeline)
MainPipeline.enqueue("test-corpus", "Pre-process test data", TestingPreProcessPipeline)
MainPipeline.enqueue("translate", "Translate Test", TranslatePipeline)
MainPipeline.enqueue("evaluate", "Evaluate Translations", EvaluationPipeline)

if __name__ == "__main__":
    naive_planner = NaivePlanner(WeightedProductOfExperts([
        RelationDirectionExpert,
        GlobalDirectionExpert,
        SplittingTendenciesExpert,
        RelationTransitionsExpert
    ]))
    # neural_planner = NeuralPlanner()
    # combined_planner = CombinedPlanner((neural_planner, naive_planner))
    config = Config(reader=WebNLGDataReader,
                    planner=naive_planner)

    res = MainPipeline.mutate({"config": config}).execute("WebNLG", cache_name="WebNLG")

    print()

    d = random.choice(res["translate"].data)
    print("Random Sample:")
    print("Graph:", d.graph.as_rdf())
    print("Plan:", d.plan)
    print("Translation:", d.hyp)
    print("Reference:  ", d.text)

    print()

    print("BLEU", res["evaluate"])
