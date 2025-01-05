from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import DurationField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import json
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from .forms import TaskForm
from .models import Task, TaskPerformer, Message, DeadlineHistory
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Avg, DurationField, ExpressionWrapper
from datetime import timedelta
@csrf_exempt
def update_performer_status(request, task_id):
    """
    Оновлення статусу виконавця і перевірка статусів всієї задачі.
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status not in ['in_progress', 'completed']:
            return JsonResponse({'error': 'Невалідний статус'}, status=400)

        # Знаходимо виконавця, який змінює статус
        performer_task = TaskPerformer.objects.filter(task=task, performer=request.user).first()

        if not performer_task:
            return JsonResponse({'error': 'Ви не є виконавцем цієї задачі'}, status=403)

        # Забороняємо змінювати статус із "Завершено" на "Виконується"
        if performer_task.status == 'completed' and new_status == 'in_progress':
            return JsonResponse({'error': 'Ви не можете повернути статус до "Виконується", якщо він вже "Завершено".'}, status=400)

        # Оновлення статусу виконавця
        if new_status == 'in_progress' and performer_task.status != 'completed':
            if not performer_task.started_at:
                performer_task.started_at = now()
        elif new_status == 'completed':
            if not performer_task.completed_at:
                performer_task.completed_at = now()
        performer_task.status = new_status
        performer_task.save()

        # Оновлення статусу задачі
        all_performers = task.performers.all()
        all_statuses = [performer.status for performer in all_performers]

        # Якщо всі виконавці "in_progress", статус задачі стає "in_progress"
        if all(status == 'in_progress' for status in all_statuses):
            if task.status != 'in_progress':
                task.status = 'in_progress'
                task.started_at = task.started_at or now()

        # Якщо всі виконавці "completed", статус задачі стає "completed"
        elif all(status == 'completed' for status in all_statuses):
            if task.status != 'completed':
                task.status = 'completed'
                task.finished_at = now()

        # Якщо статуси змішані, статус задачі не змінюється
        task.save()

        return JsonResponse({'message': 'Статус оновлено', 'task_status': task.status}, status=200)

    return JsonResponse({'error': 'Непідтримуваний метод'}, status=405)








@login_required
def task_form(request, pk=None):
    task = get_object_or_404(Task, pk=pk) if pk else None

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            form.save_m2m()  # Для збереження ManyToManyField

            # Оновлення виконавців (TaskPerformer)
            TaskPerformer.objects.filter(task=task).delete()  # Видалення старих зв'язків
            for performer in form.cleaned_data['assigned_to']:
                TaskPerformer.objects.create(task=task, performer=performer)

            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'main/task_form.html', {'form': form})




@login_required
def task_list(request):
    # Отримуємо всі задачі, які належать поточному користувачу (виконавець або власник)
    user_tasks = Task.objects.filter(
        Q(performers__performer=request.user) | Q(assigned_by=request.user)
    ).distinct()

    # Рахуємо кількість задач за статусом
    in_progress_count = user_tasks.filter(status='in_progress').count()
    not_started_count = user_tasks.filter(status='not_started').count()

    # Фільтри
    status_filter = request.GET.getlist('status')  # Фільтр по статусу
    assigned_by_filter = request.GET.get('assigned_by')  # Фільтр "Хто поставив задачу"
    priority_filter = request.GET.getlist('priority')  # Фільтр по пріоритету

    # Застосування фільтрів до задач
    tasks = user_tasks.order_by('-id')  # Сортування від більшого до меншого по ID
    if status_filter:
        tasks = tasks.filter(status__in=status_filter)
    if assigned_by_filter:
        tasks = tasks.filter(assigned_by_id=assigned_by_filter)
    if priority_filter:
        tasks = tasks.filter(priority__in=priority_filter)

    # Унікальні користувачі для фільтру "Хто поставив задачу"
    users = User.objects.filter(assigned_tasks__isnull=False).distinct()

    # Пагінація (по 7 задач на сторінку)
    paginator = Paginator(tasks, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/task_list.html', {
        'tasks': page_obj,
        'users': users,
        'in_progress_count': in_progress_count,
        'not_started_count': not_started_count,
        'page_obj': page_obj,
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Отримуємо всіх користувачів, які ще не додані як виконавці
    existing_performers = task.performers.values_list('performer_id', flat=True)
    all_users = User.objects.exclude(id__in=existing_performers)

    # Перевірка доступу
    if not TaskPerformer.objects.filter(task=task,
                                        performer=request.user).exists() and task.assigned_by != request.user:
        return JsonResponse({'error': 'Ви не маєте доступу до цієї задачі.'}, status=403)

    performers = task.performers.all()
    messages = task.messages.all().order_by('created_at')

    return render(request, 'main/task_details.html', {
        'task': task,
        'performers': performers,
        'messages': messages,
        'all_users': all_users,  # Передаємо список користувачів
    })


@csrf_exempt
def change_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status == 'completed' and task.status != 'in_progress':
            return JsonResponse({'error': 'Спочатку змініть статус на "Виконується".'}, status=400)

        task.status = new_status
        if new_status == 'in_progress':
            task.started_at = now()
        elif new_status == 'completed':
            task.finished_at = now()

        task.save()
        return JsonResponse({'success': 'Статус змінено.'}, status=200)

    return JsonResponse({'error': 'Непідтримуваний метод.'}, status=405)


@csrf_exempt
def task_add_message(request, pk):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        content = request.POST.get('content', '').strip()
        file = request.FILES.get('file')

        if not content and not file:
            return JsonResponse({'error': 'Повідомлення або файл повинні бути вказані.'}, status=400)

        # Створюємо нове повідомлення
        message = Message.objects.create(
            task=task,
            author=request.user,
            content=content,
            file=file  # Додаємо файл, якщо він є
        )

        return JsonResponse({
            'message': 'Повідомлення додано!',
            'author_name': message.author.get_full_name(),
            'author_initial': message.author.username[:1],
            'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            'content': message.content,
            'file_url': message.file.url if message.file else None,
            'file_name': message.file.name if message.file else None
        }, status=200)

    return JsonResponse({'error': 'Непідтримуваний метод.'}, status=405)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user  # Призначаємо поточного користувача
            task.save()
            form.save_m2m()  # Зберігаємо ManyToMany зв'язки
            return redirect('task_list')
    else:
        form = TaskForm()

    return render(request, 'main/task_form.html', {'form': form})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Перевірка доступу
    if not TaskPerformer.objects.filter(task=task, performer=request.user).exists() and task.assigned_by != request.user:
        return JsonResponse({'error': 'Ви не маєте доступу до цієї задачі.'}, status=403)

    performers = task.performers.all()
    messages = task.messages.all().order_by('created_at')  # Сортуємо за датою створення (старі зверху)

    # Додаємо всіх користувачів
    all_users = User.objects.all()

    return render(request, 'main/task_details.html', {
        'task': task,
        'performers': performers,
        'messages': messages,
        'all_users': all_users,  # Передаємо список користувачів у шаблон
    })
@login_required
def instructions(request):
    return render(request, 'main/instructions.html')


@login_required
def your_view(request):
    return redirect('login')  # Направляє на сторінку входу, якщо користувач не залогінений.



@login_required
def report_page(request):
    # Фільтри
    assigned_by = request.GET.get('assigned_by', None)
    status = request.GET.getlist('status')
    priority = request.GET.getlist('priority')
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    # Отримання задач
    tasks = Task.objects.all()

    if assigned_by:
        tasks = tasks.filter(assigned_by_id=assigned_by)
    if status:
        tasks = tasks.filter(status__in=status)
    if priority:
        tasks = tasks.filter(priority__in=priority)
    if start_date:
        tasks = tasks.filter(created_at__gte=start_date)
    if end_date:
        tasks = tasks.filter(deadline__lte=end_date)

    # Загальна статистика
    total_tasks = tasks.count()
    status_counts = tasks.values('status').annotate(count=Count('id'))
    avg_execution_time = tasks.filter(
        status='completed'
    ).annotate(
        execution_time=ExpressionWrapper(F('finished_at') - F('started_at'), output_field=DurationField())
    ).aggregate(average_time=Avg('execution_time'))['average_time']

    if avg_execution_time:
        avg_execution_time = timedelta(seconds=avg_execution_time.total_seconds())

    # Для фільтрів
    users = User.objects.all()

    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'status_counts': status_counts,
        'avg_execution_time': avg_execution_time,
        'users': users,
    }
    return render(request, 'main/report_page.html', context)


@login_required
def report_page(request):
    # Фільтри
    assigned_by = request.GET.get('assigned_by', None)
    performers = request.GET.getlist('performers')  # Новий фільтр по виконавцям
    status = request.GET.getlist('status')
    priority = request.GET.getlist('priority')
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    # Отримання задач
    tasks = Task.objects.all()

    if assigned_by:
        tasks = tasks.filter(assigned_by_id=assigned_by)
    if performers:
        tasks = tasks.filter(performers__performer_id__in=performers).distinct()
    if status:
        tasks = tasks.filter(status__in=status)
    if priority:
        tasks = tasks.filter(priority__in=priority)
    if start_date:
        tasks = tasks.filter(created_at__gte=start_date)
    if end_date:
        tasks = tasks.filter(deadline__lte=end_date)

    # Загальна кількість задач
    total_tasks = tasks.count()

    # Підрахунок задач за статусами
    completed_count = tasks.filter(status="completed").count()
    in_progress_count = tasks.filter(status="in_progress").count()
    not_started_count = tasks.filter(status="not_started").count()

    # Середній час виконання (тільки завершені задачі)
    avg_execution_time = tasks.filter(status="completed").annotate(
        execution_time=ExpressionWrapper(
            F("finished_at") - F("started_at"), output_field=DurationField()
        )
    ).aggregate(average_time=Avg("execution_time"))["average_time"]

    if avg_execution_time:
        avg_execution_time = timedelta(seconds=avg_execution_time.total_seconds())

    # Для фільтрів
    users = User.objects.all()

    context = {
        "tasks": tasks,
        "total_tasks": total_tasks,
        "completed_count": completed_count,
        "in_progress_count": in_progress_count,
        "not_started_count": not_started_count,
        "avg_execution_time": avg_execution_time,
        "users": users,
    }
    return render(request, "main/report_page.html", context)

from django.http import HttpResponseForbidden

def change_deadline(request, task_id):
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, pk=task_id)

            # Перевіряємо, чи користувач є автором задачі
            if task.assigned_by != request.user:
                return HttpResponseForbidden("Ви не маєте права змінювати дедлайн цієї задачі.")

            data = json.loads(request.body)
            new_deadline = data.get('deadline')

            # Логування для відлагодження
            print("Отримано дедлайн:", new_deadline)

            # Перевірка формату дати
            parsed_deadline = parse_datetime(new_deadline)
            if not parsed_deadline:
                return JsonResponse({'error': 'Невалідний формат дати'}, status=400)

            old_deadline = task.deadline
            task.deadline = parsed_deadline
            task.save()

            # Логування змін
            DeadlineHistory.objects.create(
                task=task,
                old_deadline=old_deadline,
                new_deadline=parsed_deadline,
                changed_by=request.user
            )
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Помилка: {e}")  # Логування помилки
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Непідтримуваний метод'}, status=405)




@csrf_exempt
@login_required
def add_performers(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_id)

        # Перевірка доступу: тільки автор задачі може додавати виконавців
        if task.assigned_by != request.user:
            return JsonResponse({'error': 'Ви не маєте права додавати виконавців.'}, status=403)

        # Перевірка статусу задачі
        if task.status == 'completed':
            # Посилання на створення нової задачі
            create_task_url = reverse('task_create')
            return JsonResponse({
                'error': 'Задача завершена. Додавання виконавців неможливе.',
                'create_task_url': create_task_url
            }, status=400)

        data = json.loads(request.body)
        performer_ids = data.get('performers', [])

        # Перевіряємо, чи всі виконавці існують
        performers = User.objects.filter(id__in=performer_ids)
        if not performers.exists():
            return JsonResponse({'error': 'Невалідні ID користувачів.'}, status=400)

        # Додаємо виконавців до задачі
        for performer in performers:
            TaskPerformer.objects.get_or_create(task=task, performer=performer)

        return JsonResponse({'success': 'Виконавців додано.'}, status=200)

    return JsonResponse({'error': 'Непідтримуваний метод.'}, status=405)
