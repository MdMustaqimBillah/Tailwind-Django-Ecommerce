from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Carousel
from .forms import CarouselForm

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'Access denied! Admin access only.')
        return redirect('product_list')

from django.views.generic import CreateView  # Change this import

class CarouselCreateView(LoginRequiredMixin, SuperUserRequiredMixin, CreateView):  # Change to CreateView
    model = Carousel
    form_class = CarouselForm
    template_name = 'carousel/add_carousel.html'
    success_url = reverse_lazy('product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Carousel image added successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid form data. Please provide valid data.')
        return super().form_invalid(form)

class CarouselUpdateView(LoginRequiredMixin, SuperUserRequiredMixin, UpdateView):
    model = Carousel
    form_class = CarouselForm
    template_name = 'carousel/add_carousel.html'
    success_url = reverse_lazy('product_list')
    context_object_name = 'carousel'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Carousel image updated successfully.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid form data. Please provide valid data.')
        return super().form_invalid(form)
        
class CarouselListView(LoginRequiredMixin, SuperUserRequiredMixin, ListView):
    model = Carousel
    template_name = 'carousel/carousel_list.html'
    context_object_name = 'carousels'
    
    def get_queryset(self):
        return Carousel.objects.all()

class CarouselDeleteView(LoginRequiredMixin, SuperUserRequiredMixin, DeleteView):
    model = Carousel
    success_url = reverse_lazy('Carousel:carousel_list')
    
    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, 'Successfully deleted carousel.')
        return super().delete(request, *args, **kwargs)