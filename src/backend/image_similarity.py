import joblib
import os
import torch
import torchvision.transforms as transforms

from torch.autograd import Variable
from PIL import Image
from triplet_net import TripletNet, resnet18, model_urls

class ImageSimilarity:
    def __init__(self, data_path: str, images_path: str):
        self.data_path = data_path
        self.images_path = images_path
        self.neighbour_model = joblib.load(os.path.join(data_path, "neighbor_model.joblib"))

        self.triple_net = TripletNet(resnet18(model_urls, data_path))
        checkpoint = torch.load(os.path.join(data_path, "deep_ranking.pth.tar"))
        self.triple_net.load_state_dict(checkpoint["state_dict"])
        self.triple_net.eval()

    @staticmethod
    def _transform_test_img(img):
        transform_test = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
        return transform_test(img)

    @staticmethod
    def _gen_embedding(net, data):
        data = Variable(data)

        embedded, _, _ = net(data, data, data)
        embedded_numpy = embedded.data.cpu().numpy()

        return embedded_numpy

    def _load_triplet_images(self):
        triplet_images = []
        for line in open(os.path.join(self.data_path, "triplets.txt")):
            line_array = line.split(",")
            if line_array[0] not in triplet_images:
                triplet_images.append(line_array[0])

        return triplet_images

    def get_similar_images(self, query_image_id: str) -> list[dict]:
        similar_images = list()

        # Load the image
        query_image_path = os.path.join(self.images_path, f"{query_image_id}.jpg")
        query_img = self._transform_test_img(Image.open(query_image_path).convert("RGB")).reshape(1, 3, 224, 224)

        # Execute query
        query_embed = self._gen_embedding(self.triple_net, query_img)
        predictions = self.neighbour_model.kneighbors(query_embed, return_distance=True)

        merged_list = [(predictions[1][0][i], predictions[0][0][i]) for i in range(0, len(predictions[0][0]))]

        # Triplet images
        training_images = self._load_triplet_images()

        for image_id, score in merged_list:
            similar_images.append({
                "image_id": os.path.basename(training_images[int(image_id)]).replace(".jpg", ""),
                "score": float(score)
            })

        return similar_images



