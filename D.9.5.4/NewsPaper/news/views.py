# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .forms import PostForm
from .models import Post
from .filters import PostFilter
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.mail import send_mail

def notify_users_signup(sender, instance, created, **kwargs):
    send_mail(
        subject='Регистрация на портале BorisovNews',
        message='Спасибо, что зарегистрировались на нашем новостном портале! ' + instance.username,
        from_email='aleksandr720604@yandex.by',
        recipient_list=[instance.email],
    )

# коннектим наш сигнал к функции обработчику и указываем модель User
post_save.connect(notify_users_signup, sender=User)



class Welcome(LoginRequiredMixin, TemplateView):
    template_name = 'new_welcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context




class PostList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-time_in'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'news'
    paginate_by = 5  # вот так мы можем указать количество записей на странице

    # Переопределяем функцию получения списка товаров
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        #print(self.filterset.qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        #print(context)
        return context

class PostSearch(PostList):
    template_name = 'news_search.html'



class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — product.html
    template_name = 'new.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'new'

    # Добавляем новое представление для создания товаров.
class PostCreate(LoginRequiredMixin, CreateView):
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'new_edit.html'

    login_url = '/sign/login/'
    #redirect_field_name = 'post_create'

#    def form_valid(self, form):
        #post = form.save(commit=False)

        #print('данные')
        #print(self.request.user)
        #request.method == 'GET'
        #path_type = self.request.META.get['PATH_INFO']

       # print(path_type)
       # if path_type == '/news/create/':
       #     post.type_post = 'NE'
       # if path_type == '/articles/create/':
       #     post.type_post = 'AR'
       # return super().form_valid(form)


# Добавляем представление для изменения товара.
class PostUpdate(LoginRequiredMixin,UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'new_edit.html'
    login_url = '/sign/login/'

class PostDelete(DeleteView):
    model = Post
    template_name = 'new_delete.html'
    success_url = reverse_lazy('post_list')


#def create_post(request):
#    print(request)
#    if request.method == 'POST':
#        form = PostForm(request.POST)
#        form.save()
#        return HttpResponseRedirect('/news/')
#
#    form = PostForm()
#    return render(request, 'new_edit.html', {'form':form})
