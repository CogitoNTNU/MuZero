import torch
from torch.distributions.dirichlet import Dirichlet
from torch.testing import assert_close
from src.utils.tensor_utils import normalize_policy_values_with_noise


"""
Comment on the use of torch.testing.assert_close:
The torch.testing.assert_close function is used to compare two tensors for approximate equality.
Floating point operations can sometimes lead to small differences in the values of two tensors that should be equal.
Additionally, the function is checking that both tensors have the same shape, dtype, and device.
"""

alpha = 0.3
epsilon = 0.75

def test_normalize_policy_values_with_noise_basic():
    """
    Tests basic functionality of normalize_policy_values to ensure it normalizes
    policy values correctly for specified legal actions.
    """
    torch.manual_seed(75)

    nn_policy_values = torch.tensor([-0.4, 0, 0.7, 0], dtype=torch.float)
    legal_actions = torch.tensor([1, 3], dtype=torch.long)
    
    expected_output = nn_policy_values.clone()

    softmax_tensor = torch.tensor([0.5, 0.5]) # Expected softmax values for indices 1 and 3
    alpha_tensor = torch.tensor([alpha, alpha])
    noise = Dirichlet(alpha_tensor).sample() # Seed 75 -> [0.4242, 0.5758]
    expected_new_values = softmax_tensor * epsilon + noise * (1 - epsilon) ## Combine the probabilities and noise tensors to form the final policy values
    expected_output[legal_actions] = expected_new_values

    normalize_policy_values_with_noise(nn_policy_values, legal_actions, noise, epsilon) # Modifies nn_policy_values in place

    assert_close(nn_policy_values, expected_output)

def test_normalize_policy_values_with_noise_all_legal():
    """
    Tests the normalize_policy_values_with_noise function when all actions are legal,
    ensuring the entire tensor is normalized.
    """
    torch.manual_seed(75)

    nn_policy_values = torch.tensor([0.1, 0.2, 0.3, 0.4], dtype=torch.float)
    legal_actions = torch.tensor([0, 1, 2, 3], dtype=torch.long)
    expected_output = nn_policy_values.clone()

    softmax_tensor = torch.softmax(nn_policy_values, dim=0)
    alpha_tensor = torch.tensor([alpha, alpha, alpha, alpha])
    noise = Dirichlet(alpha_tensor).sample() # Seed 75 -> [0.3911, 0.5310, 0.0039, 0.0740]
    expected_new_values = softmax_tensor * epsilon + noise * (1 - epsilon) ## Combine the probabilities and noise tensors to form the final policy values
    
    expected_output = expected_new_values

    normalize_policy_values_with_noise(nn_policy_values, legal_actions, noise, epsilon) # Modifies nn_policy_values in place

    assert_close(nn_policy_values, expected_output)

def test_normalize_policy_values_with_noise_no_legal():
    """
    Tests the normalize_policy_values_with_noise function with an empty legal_actions tensor,
    expecting the original nn_policy_values tensor to remain unchanged.
    """
    torch.manual_seed(75)

    nn_policy_values = torch.tensor([1.0, 2.0, 3.0, 4.0], dtype=torch.float)
    legal_actions = torch.tensor([], dtype=torch.long)
    
    noise = Dirichlet(torch.tensor([])).sample() # Empty tensor
    expected_output = nn_policy_values.clone()

    normalize_policy_values_with_noise(nn_policy_values, legal_actions, noise, epsilon)

    torch.testing.assert_close(nn_policy_values, expected_output)